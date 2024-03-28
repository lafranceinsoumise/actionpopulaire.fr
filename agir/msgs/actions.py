from django.db import connection
from django.db.models import (
    OuterRef,
    Subquery,
    Exists,
    Q,
    Count,
    Value,
)
from django.db.models.functions import Coalesce
from django.utils import timezone

from agir.activity.models import Activity
from agir.groups.models import Membership
from agir.msgs.models import (
    SupportGroupMessageRecipient,
    SupportGroupMessage,
    SupportGroupMessageComment,
)
from agir.notifications.models import Subscription
from agir.people.models import Person

RECENT_COMMENT_LIMIT = 4


"""Pour simplifier le raisonnement, on compte séparément les messages et commentaires non lus.

Cela correspond aux deux sous-requêtes WITH.
"""
UNREAD_COUNT_REQUEST = f"""
WITH messages AS (
    SELECT COUNT(*) AS total FROM msgs_supportgroupmessage message
      JOIN people_person message_author ON message_author.id = message.author_id
      JOIN authentication_role message_author_role ON message_author_role.id = message_author.role_id
      JOIN groups_membership membership
        ON membership.supportgroup_id = message.supportgroup_id AND membership.person_id = %(person_id)s
      LEFT JOIN msgs_supportgroupmessagerecipient recipient
        ON recipient.message_id = message.id AND recipient.recipient_id = %(person_id)s
    -- exclude deleted messages
    WHERE NOT message.deleted
    -- exclude messages of inactive users
    AND message_author_role.is_active
    -- ensure user has the required membership_type in the group
    AND membership.membership_type >= message.required_membership_type
    -- exclude own messages
    AND message.author_id != %(person_id)s
    -- include only messages created after joining the group
    AND message.created > membership.created
    -- include only messages not read (no need to control for muting, since a muted message has been seen anyway)
    AND recipient.id IS NULL
),
comments AS (
    SELECT COUNT(*) AS total FROM msgs_supportgroupmessagecomment comment
      JOIN msgs_supportgroupmessage message ON message.id = comment.message_id
      JOIN people_person message_author ON message_author.id = message.author_id
      JOIN authentication_role message_author_role ON message_author_role.id = message_author.role_id
      JOIN people_person comment_author ON comment_author.id = comment.author_id
      JOIN authentication_role comment_author_role ON comment_author_role.id = comment_author.role_id
      -- left join, because person can see messages she sent to other groups
      LEFT JOIN groups_membership membership
        ON membership.supportgroup_id = message.supportgroup_id AND membership.person_id = %(person_id)s
      LEFT JOIN msgs_supportgroupmessagerecipient recipient
        ON recipient.message_id = message.id AND recipient.recipient_id = %(person_id)s
    -- exclude comments on deleted messages and deleted comments
    WHERE NOT message.deleted
    AND NOT comment.deleted
    -- exclude own comments
    AND comment.author_id != %(person_id)s
    -- exclude messages and comments of inactive users
    AND message_author_role.is_active
    AND comment_author_role.is_active
    -- only on messages the person can see: either they have the required membership_type, or they are the message's
    -- author
    AND (
      membership.membership_type >= message.required_membership_type
      OR (
        membership.membership_type IS NULL
        AND message.author_id = %(person_id)s
      )
    )
    -- exclude muted messages (coalescing because recipient is null if the message has never been seen)
    AND NOT COALESCE(recipient.muted, FALSE)
    -- include only messages created after both the person joined the group AND the last time the person saw the message
    -- note that while recipient.modified might be null (if the message has never been seen). PostgreSQL's GREATEST
    -- ignore NULL values.
    -- message.created is added as a default value for cases where both recipient and membership are NULL
    AND comment.created > GREATEST(recipient.modified, membership.created, message.created)
)
SELECT messages.total + comments.total AS total
FROM messages JOIN comments ON true;
"""

USER_MESSAGES_BASE_REQUEST = """
  SELECT
    message.id,
    message.author_id,
    COALESCE(
      (
        SELECT comment.created
        FROM msgs_supportgroupmessagecomment AS comment
        WHERE comment.message_id = message.id
        ORDER BY comment.created DESC
        LIMIT 1
      ),
      message.created
    ) AS last_comment_date
  FROM msgs_supportgroupmessage AS message
"""

USER_MESSAGES_WITH_REQUEST = f"""
WITH message AS (
  {USER_MESSAGES_BASE_REQUEST}
  JOIN groups_membership AS membership ON (
    membership.supportgroup_id = message.supportgroup_id
    AND membership.person_id = %(person_id)s
  )
  WHERE
    membership.membership_type >= message.required_membership_type
    AND NOT message.deleted
    -- s'assurer qu'on ne renvoie pas de commentaire inclus dans l'autre requête
    AND message.author_id != %(person_id)s

  UNION ALL

  {USER_MESSAGES_BASE_REQUEST}
  WHERE author_id = %(person_id)s
    AND NOT message.deleted
)
"""

"""Requête faite main pour récupérer de façon performante les identifiants des derniers messages.

Pour que la base de données utilise les index (plutôt que des scans séquentiels), les techniques suivantes sont
employées :
- utiliser une sous-requête `SELECT ... ORDER BY ... LIMIT 1` pour récupérer la date du dernier commentaire plutôt
  qu'une agrégation MAX, ce qui permet d'utiliser l'index (message_id, created) sur la table des commentaires
- séparer la recherche des messages pour lesquels on est autorisé grâce à son statut de membre de ceux dont on est
  l'auteur pour permettre à postgresql d'utiliser l'index approprié pour chaque sous-requête. UNION ALL permet
  d'éviter une déduplication inutile si on fait attention à exclure les messages dont on est l'auteur dans le cas 1.
- Classer les résultats dans un second temps seulement, par une autre requête, et appliquer la limite à ce moment-là.
- Finalement, réaliser la jointure sur les auteurs dans la dernière requête seulement, ce qui permet de s'assurer
  qu'elle n'est réalisée que pour le petit nombre de résultats couverts par le LIMIT.
"""
USER_MESSAGES_IDS_REQUEST = f"""
{USER_MESSAGES_WITH_REQUEST}

SELECT
  message.id,
  last_comment_date
FROM message
JOIN people_person AS author ON message.author_id = author.id
JOIN authentication_role AS role ON role.id = author.role_id
WHERE role.is_active
ORDER BY message.last_comment_date DESC
OFFSET %(offset)s
LIMIT %(limit)s;"""

USER_MESSAGES_COUNT_REQUEST = f"""
{USER_MESSAGES_WITH_REQUEST}

SELECT COUNT(message.id) FROM message
JOIN people_person AS author ON message.author_id = author.id
JOIN authentication_role AS role ON role.id = author.role_id
WHERE role.is_active;
"""


USER_MESSAGES_READ_ALL_REQUEST = f"""
INSERT INTO msgs_supportgroupmessagerecipient (message_id, recipient_id, created, modified, muted)
(
  {USER_MESSAGES_WITH_REQUEST}

  SELECT
    id,
    %(person_id)s,
    %(now)s,
    %(now)s,
    FALSE
  FROM message
)
ON CONFLICT (message_id, recipient_id)
DO UPDATE SET modified = %(now)s;
"""


def update_recipient_message(message, recipient):
    obj, created = SupportGroupMessageRecipient.objects.update_or_create(
        message=message,
        recipient=recipient,
    )
    return obj, created


def read_all_user_messages(person):
    """Indique tous les messages de l'utilisateur comme lus"""
    with connection.cursor() as cursor:
        cursor.execute(
            USER_MESSAGES_READ_ALL_REQUEST,
            {"person_id": person.id, "now": timezone.now()},
        )


def get_unread_message_count(person):
    """Retourne le nombre de messages non lus de la personne

    Cette requête est executée sur chaque page, donc elle doit renvoyer une réponse rapide.
    """

    with connection.cursor() as cursor:
        cursor.execute(UNREAD_COUNT_REQUEST, {"person_id": person.id})
        return cursor.fetchone()[0]


def get_message_unread_comment_count(person: Person, message: SupportGroupMessage):
    try:
        membership = Membership.objects.get(
            person=person, supportgroup_id=message.supportgroup_id
        )
    except Membership.DoesNotExist:
        return 0

    if hasattr(message, "last_reading_date"):
        last_reading_date = message.last_reading_date
    else:
        recipient = SupportGroupMessageRecipient.objects.filter(
            recipient=person, message=message
        ).first()
        last_reading_date = recipient and recipient.modified

    if last_reading_date:
        cutoff = max(last_reading_date, membership.created)
    else:
        cutoff = membership.created

    return (
        message.comments.annotate(
            last_reading_date=Subquery(
                SupportGroupMessageRecipient.objects.filter(
                    recipient=person, message=message
                ).values("modified")
            )
        )
        .filter(created__gte=cutoff, deleted=False, author__role__is_active=True)
        .exclude(author=person)
        .count()
    )


def get_user_messages_count(person):
    with connection.cursor() as cursor:
        cursor.execute(USER_MESSAGES_COUNT_REQUEST, {"person_id": person.id})
        return cursor.fetchone()[0]


def get_base_user_messages_qs(person):
    return SupportGroupMessage.objects.with_serializer_prefetch().annotate(
        # sous-requête en doublon, mais je ne vois pas d'autre solution avec Django
        last_reading_date=Subquery(
            SupportGroupMessageRecipient.objects.filter(
                recipient=person, message=OuterRef("id")
            ).values("modified")
        ),
        muted=Coalesce(
            Subquery(
                SupportGroupMessageRecipient.objects.filter(
                    recipient=person, message=OuterRef("id")
                ).values("muted")
            ),
            Value(False),
        ),
        joined_group=Subquery(
            Membership.objects.filter(
                person=person,
                supportgroup=OuterRef("supportgroup_id"),
                membership_type__gte=OuterRef("required_membership_type"),
            ).values("created")
        ),
        comment_count=Coalesce(
            Subquery(
                SupportGroupMessageComment.objects.filter(
                    message=OuterRef("id"),
                    deleted=False,
                    author__role__is_active=True,
                )
                .values("message_id")
                .order_by("message_id")
                .annotate(c=Count("id"))
                .values("c")
            ),
            0,
        ),
        unread_comment_count=Coalesce(
            Subquery(
                SupportGroupMessageComment.objects.filter(
                    message=OuterRef("id"),
                    deleted=False,
                    author__role__is_active=True,
                    created__gte=Coalesce(
                        OuterRef("last_reading_date"), OuterRef("joined_group")
                    ),
                )
                .exclude(author=person)
                .values("message_id")
                .order_by("message_id")
                .annotate(c=Count("id"))
                .values("c")
            ),
            0,
        ),
    )


def get_user_messages(person, start=0, stop=20):
    with connection.cursor() as cursor:
        cursor.execute(
            USER_MESSAGES_IDS_REQUEST,
            {
                "person_id": person.id,
                "offset": start,
                "limit": stop - start,
            },
        )
        results = cursor.fetchall()

    message_ids = [m for m, _ in results]

    messages = list(get_base_user_messages_qs(person).filter(id__in=message_ids))

    messages_map = {m.id: m for m in messages}

    # on rajoute la date de dernier commentaire à partir de la dernière requête
    for id, last_update in results:
        # cas extrême où un des messages a été supprimé entre la première et la deuxième requête
        if id in messages:
            messages[id].last_update = last_update

    # on remet les messages dans l'ordre
    messages = [messages_map[id] for id in message_ids if id in messages_map]

    # on précharge les commentaires correspondants
    prefetch_recent_comments(messages)

    return messages


def get_comment_recipients(comment: SupportGroupMessageComment):
    """Récupềre la liste des personnes destinataires d'un commentaire

    Le queryset renvoyé exclut les personnes qui ont mis le message en silencieux
    """
    return (
        Person.objects.annotate(
            muted=Exists(
                SupportGroupMessageRecipient.objects.filter(
                    message=comment.message, recipient=OuterRef("id"), muted=True
                )
            ),
            is_comment_author=Exists(
                SupportGroupMessageComment.objects.active().filter(
                    message=comment.message,
                    author=OuterRef("id"),
                )
            ),
        ).filter(
            memberships__supportgroup__id=comment.message.supportgroup_id,
            memberships__membership_type__gte=comment.message.required_membership_type,
            muted=False,
        )
        # on ne veut pas envoyer de notification à l'auteur du commentaire !
        .exclude(id=comment.author_id)
    )


def get_comment_participants(comment: SupportGroupMessageComment):
    """Récupère la liste des personnes participantes à un message

    Le queryset renvoyé exclut les personnes qui ont mis le message en silencieux
    """

    all_recipients = get_comment_recipients(comment)
    return all_recipients.annotate(
        with_subscription=Exists(
            Subscription.objects.filter(
                membership__supportgroup_id=comment.message.supportgroup_id,
                person_id=OuterRef("id"),
                type=Subscription.SUBSCRIPTION_PUSH,
                # pour les participants le type pertinent est TYPE_NEW_COMMENT_RESTRICTED
                activity_type=Activity.TYPE_NEW_COMMENT_RESTRICTED,
            )
        )
    ).filter(
        Q(with_subscription=True)
        & (Q(is_comment_author=True) | Q(id=comment.message.author_id))
    )


def get_comment_other_recipients(comment: SupportGroupMessageComment):
    all_recipients = get_comment_recipients(comment)
    return all_recipients.annotate(
        with_subscription=Exists(
            Subscription.objects.filter(
                membership__supportgroup_id=comment.message.supportgroup_id,
                person_id=OuterRef("id"),
                type=Subscription.SUBSCRIPTION_PUSH,
                # attention, type comment tout court ici !
                activity_type=Activity.TYPE_NEW_COMMENT,
            )
        )
    ).filter(
        Q(with_subscription=True)
        & ~(Q(is_comment_author=True) | Q(id=comment.message.author_id))
    )


def get_event_messages(event, person):
    return get_base_user_messages_qs(person).filter(
        Q(joined_group__isnull=False) | Q(author=person), linked_event=event
    )


def filter_with_subscription(qs, *, comment, subscription_type, activity_type):
    return qs.annotate(
        with_subscription=Exists(
            Subscription.objects.filter(
                membership__supportgroup_id=comment.message.supportgroup_id,
                person_id=OuterRef("id"),
                type=subscription_type,
                # attention, type comment tout court ici !
                activity_type=activity_type,
            )
        )
    ).filter(with_subscription=True)


def prefetch_recent_comments(qs):
    if len(qs) == 0:
        return qs

    comments = SupportGroupMessageComment.objects.raw(
        """
        WITH comments AS (
            SELECT
              id,
              created,
              modified,
              message_id,
              author_id,
              text,
              attachment_id,
              deleted,
              row_number() OVER (PARTITION BY message_id ORDER BY created DESC) AS rang
            FROM msgs_supportgroupmessagecomment
            WHERE
              message_id IN %(message_ids)s
              AND NOT deleted
        )
        SELECT * from comments WHERE rang < %(nb_comments)s;
        """,
        {"message_ids": tuple(m.id for m in qs), "nb_comments": RECENT_COMMENT_LIMIT},
    )
    comments_by_message = {}
    for c in comments:
        comments_by_message.setdefault(c.message_id, [])
        comments_by_message[c.message_id].append(c)

    for message in qs:
        message.recent_comments = comments_by_message.get(message.id, [])
