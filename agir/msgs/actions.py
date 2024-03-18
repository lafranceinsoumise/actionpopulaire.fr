from django.db import connection
from django.db.models import (
    OuterRef,
    Subquery,
    Exists,
    Q,
    Max,
    DateTimeField,
    F,
    Count,
    Value,
)
from django.db.models.functions import Greatest, Coalesce

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

# Requête alternative : le nombre de messages qui ont au moins un commentaire nouveau / non utilisé pour le moment
MESSAGES_WITH_UNREAD_COMMENTS_COUNT_REQUEST = """
SELECT COUNT(*) FROM msgs_supportgroupmessage message
 LEFT JOIN msgs_supportgroupmessagerecipient recipient ON recipient.message_id = message.id
 JOIN groups_membership membership ON message.supportgroup_id = membership.supportgroup_id 
 WHERE recipient.recipient_id = '74178da8-d8d9-422e-b16f-6aa2b253a9de'
 AND membership.person_id = '74178da8-d8d9-422e-b16f-6aa2b253a9de'
 AND membership.membership_type >= message.required_membership_type
 AND (
   recipient.id IS NULL
OR GREATEST(recipient.modified, membership.modified) < COALESCE(
  (SELECT MAX(comment.modified) FROM msgs_supportgroupmessagecomment comment WHERE comment.message_id = message.id), message.modified)
 );
"""


"""Pour simplifier le raisonnement, on compte séparément les messages et les commentaires

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
    -- exclude muted messages (coalescing because recipient is null if the message has never been seen)
    AND NOT COALESCE(recipient.muted, FALSE)
    -- include only messages created after joining the group
    AND message.created > membership.created
    -- include only messages not read
    AND recipient.id IS NULL
),
comments AS (
    SELECT COUNT(*) AS total FROM msgs_supportgroupmessagecomment comment
      JOIN msgs_supportgroupmessage message ON message.id = comment.message_id
      JOIN people_person message_author ON message_author.id = message.author_id
      JOIN authentication_role message_author_role ON message_author_role.id = message_author.role_id
      JOIN people_person comment_author ON comment_author.id = comment.author_id
      JOIN authentication_role comment_author_role ON comment_author_role.id = comment_author.role_id
      JOIN groups_membership membership
        ON membership.supportgroup_id = message.supportgroup_id AND membership.person_id = %(person_id)s
      LEFT JOIN msgs_supportgroupmessagerecipient recipient 
        ON recipient.message_id = message.id AND recipient.recipient_id = %(person_id)s
    -- exclude comments on deleted messages and deleted comments
    WHERE NOT message.deleted
    AND NOT comment.deleted
    -- exclude messages and comments of inactive users
    AND message_author_role.is_active
    AND comment_author_role.is_active
    -- do not include messages whose author is current user to avoid double counting
    AND message.author_id != %(person_id)s
    -- include only messages current user is allowed to see
    AND membership.membership_type >= message.required_membership_type
    -- exclude own comments
    AND comment.author_id != %(person_id)s
    -- exclude muted messages (coalescing because recipient is null if the message has never been seen)  
    AND NOT COALESCE(recipient.muted, FALSE)
    -- include only messages created after both the person joined the group AND the last time the person saw the message
    -- note that while recipient.modified might be null (if the message has never been seen), PostgreSQL's GREATEST
    -- ignore NULL values 
    AND comment.created > GREATEST(recipient.modified, membership.created)
),
comments_on_ownmessages AS (
    SELECT COUNT(*) AS total FROM msgs_supportgroupmessagecomment comment
      JOIN people_person comment_author ON comment_author.id = comment.author_id
      JOIN authentication_role comment_author_role ON comment_author_role.id = comment_author.role_id
      JOIN msgs_supportgroupmessage message ON message.id = comment.message_id
      LEFT JOIN msgs_supportgroupmessagerecipient recipient ON recipient.message_id = message.id
    -- exclude comments on deleted messages and deleted comments
    WHERE NOT message.deleted
    AND NOT comment.deleted
    -- exclude comments of inactive users (we assume the reader is active)
    AND comment_author_role.is_active
    -- limit to messages authored by the person
    AND message.author_id = %(person_id)s
    -- exclude muted messages (coalescing because recipient is null if the message has never been seen)  
    AND NOT COALESCE(recipient.muted, FALSE)  
    -- include only messages modified since seen, coalescing on the creation of the message
    AND comment.created > COALESCE(recipient.modified, message.created) 
)
SELECT messages.total + comments.total + comments_on_ownmessages.total AS total 
FROM messages JOIN comments ON true JOIN comments_on_ownmessages ON true;
"""


def update_recipient_message(message, recipient):
    obj, created = SupportGroupMessageRecipient.objects.update_or_create(
        message=message,
        recipient=recipient,
    )
    return obj, created


def get_viewables_messages(person):
    """Retourne tous les messages visibles par l'utilisateur

    Un message est visible si :
    - il est dans un groupe d'action dont l'utilisateur est membre
    - son champ required_membership_type est inférieur au champ membership_type du Membership de la personne
    """
    return (
        SupportGroupMessage.objects.active()
        .annotate(
            has_required_membership_type=Exists(
                person.memberships.filter(
                    supportgroup_id=OuterRef("supportgroup_id"),
                    membership_type__gte=OuterRef("required_membership_type"),
                )
            )
        )
        .filter(Q(author_id=person.id) | Q(has_required_membership_type=True))
    )


def get_viewable_messages_ids(person):
    message_ids = get_viewables_messages(person).values_list("id", flat=True)
    return list(set(message_ids))


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


def get_user_messages(person):
    return (
        SupportGroupMessage.objects.active()
        .select_related("supportgroup", "author")
        .annotate(
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
                    person=person, supportgroup=OuterRef("supportgroup_id")
                ).values("created")
            ),
            last_update=Greatest(
                Max("comments__created"), "created", output_field=DateTimeField()
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
        .filter(
            # user has required membership type
            Q(
                supportgroup__memberships__person=person,
                supportgroup__memberships__membership_type__gte=F(
                    "required_membership_type"
                ),
            )
            # or user is author of the message
            | Q(author=person),
        )
        .order_by("-last_update", "-created")
    )


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
              image,
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
