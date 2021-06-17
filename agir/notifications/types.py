class SubscriptionType:

    TYPE_REFERRAL = "referral-accepted"

    # PERSON/EVENT TYPES
    TYPE_NEW_ATTENDEE = "new-attendee"
    TYPE_EVENT_UPDATE = "event-update"
    TYPE_CANCELLED_EVENT = "cancelled-event"
    TYPE_WAITING_LOCATION_EVENT = "waiting-location-event"
    TYPE_WAITING_LOCATION_GROUP = "waiting-location-group"
    TYPE_EVENT_SUGGESTION = "event-suggestion"
    TYPE_ANNOUNCEMENT = "announcement"

    # GROUP TYPES
    TYPE_NEW_REPORT = "new-report"
    TYPE_NEW_EVENT_MYGROUPS = "new-event-mygroups"
    TYPE_GROUP_INVITATION = "group-invitation"
    TYPE_NEW_MEMBER = "new-member"
    TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER = "group-membership-limit-reminder"
    TYPE_GROUP_INFO_UPDATE = "group-info-update"
    TYPE_NEW_MESSAGE = "new-message"
    TYPE_NEW_COMMENT = "new-comment"
    TYPE_GROUP_CREATION_CONFIRMATION = "group-creation-confirmation"
    TYPE_ACCEPTED_INVITATION_MEMBER = "accepted-invitation-member"
    TYPE_TRANSFERRED_GROUP_MEMBER = "transferred-group-member"
    TYPE_NEW_MEMBERS_THROUGH_TRANSFER = "new-members-through-transfer"

    # TODO
    TYPE_GROUP_COORGANIZATION_INFO = "group-coorganization-info"
    TYPE_GROUP_COORGANIZATION_ACCEPTED = "group-coorganization-accepted"
    TYPE_GROUP_COORGANIZATION_INVITE = "group-coorganization-invite"
    TYPE_WAITING_PAYMENT = "waiting-payment"

    # MANDATORY TYPES
    MANDATORY_EMAIL_TYPES = (
        TYPE_CANCELLED_EVENT,
        TYPE_WAITING_PAYMENT,
        # GROUP
        TYPE_TRANSFERRED_GROUP_MEMBER,
        TYPE_GROUP_INVITATION,
        TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER,
    )
    MANDATORY_PUSH_TYPES = (
        TYPE_CANCELLED_EVENT,
        TYPE_WAITING_PAYMENT,
        # GROUP
        TYPE_TRANSFERRED_GROUP_MEMBER,
        TYPE_GROUP_INVITATION,
        TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER,
    )

    # DEFAULT PERSON/EVENT TYPES
    DEFAULT_PERSON_EMAIL_TYPES = [
        TYPE_EVENT_SUGGESTION,
        TYPE_EVENT_UPDATE,
        TYPE_NEW_ATTENDEE,
        TYPE_WAITING_LOCATION_EVENT,
    ]
    DEFAULT_PERSON_PUSH_TYPES = [
        TYPE_EVENT_SUGGESTION,
        TYPE_EVENT_UPDATE,
        TYPE_NEW_ATTENDEE,
        TYPE_WAITING_LOCATION_EVENT,
    ]

    # DEFAULT GROUP TYPES
    DEFAULT_GROUP_EMAIL_TYPES = [
        TYPE_NEW_EVENT_MYGROUPS,
        TYPE_GROUP_COORGANIZATION_INFO,
        TYPE_GROUP_INFO_UPDATE,
        TYPE_NEW_MESSAGE,
        TYPE_NEW_COMMENT,
        TYPE_NEW_REPORT,
        TYPE_NEW_MEMBER,
        TYPE_ACCEPTED_INVITATION_MEMBER,
        TYPE_NEW_MEMBERS_THROUGH_TRANSFER,
        TYPE_WAITING_LOCATION_GROUP,
        TYPE_GROUP_COORGANIZATION_INVITE,
        TYPE_GROUP_CREATION_CONFIRMATION,
        TYPE_GROUP_COORGANIZATION_ACCEPTED,
    ]
    DEFAULT_GROUP_PUSH_TYPES = [
        TYPE_NEW_EVENT_MYGROUPS,
        TYPE_GROUP_COORGANIZATION_INFO,
        TYPE_GROUP_INFO_UPDATE,
        TYPE_NEW_MESSAGE,
        TYPE_NEW_COMMENT,
        TYPE_NEW_REPORT,
        TYPE_NEW_MEMBER,
        TYPE_ACCEPTED_INVITATION_MEMBER,
        TYPE_NEW_MEMBERS_THROUGH_TRANSFER,
        TYPE_WAITING_LOCATION_GROUP,
        TYPE_GROUP_COORGANIZATION_INVITE,
        TYPE_GROUP_CREATION_CONFIRMATION,
        TYPE_GROUP_COORGANIZATION_ACCEPTED,
    ]

    DISPLAYED_TYPES = (
        TYPE_GROUP_INVITATION,
        TYPE_NEW_MEMBER,
        TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER,
        TYPE_GROUP_INFO_UPDATE,
        TYPE_NEW_ATTENDEE,
        TYPE_EVENT_UPDATE,
        TYPE_NEW_EVENT_MYGROUPS,
        TYPE_NEW_REPORT,
        TYPE_CANCELLED_EVENT,
        TYPE_REFERRAL,
        TYPE_GROUP_COORGANIZATION_INFO,
        TYPE_ACCEPTED_INVITATION_MEMBER,
        TYPE_GROUP_COORGANIZATION_ACCEPTED,
        TYPE_WAITING_LOCATION_EVENT,
        TYPE_GROUP_COORGANIZATION_INVITE,
        TYPE_WAITING_LOCATION_GROUP,
        TYPE_WAITING_PAYMENT,
        TYPE_GROUP_CREATION_CONFIRMATION,
        TYPE_TRANSFERRED_GROUP_MEMBER,
        TYPE_NEW_MEMBERS_THROUGH_TRANSFER,
        TYPE_NEW_MESSAGE,
        TYPE_NEW_COMMENT,
        TYPE_EVENT_SUGGESTION,
        TYPE_ANNOUNCEMENT,
        # Old required action types :
        TYPE_WAITING_PAYMENT,
        TYPE_GROUP_INVITATION,
        TYPE_NEW_MEMBER,
        TYPE_WAITING_LOCATION_GROUP,
        TYPE_GROUP_COORGANIZATION_INVITE,
        TYPE_WAITING_LOCATION_EVENT,
        TYPE_GROUP_CREATION_CONFIRMATION,
        TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER,
    )

    TYPE_CHOICES = (
        (TYPE_WAITING_PAYMENT, "Paiement en attente"),
        (TYPE_GROUP_INVITATION, "Invitation à un groupe"),
        (TYPE_NEW_MEMBER, "Nouveau membre dans le groupe"),
        (
            TYPE_GROUP_MEMBERSHIP_LIMIT_REMINDER,
            "Les membres du groupes sont de plus en plus nombreux",
        ),
        (TYPE_NEW_MESSAGE, "Nouveau message dans un de vos groupes"),
        (TYPE_NEW_COMMENT, "Nouveau commentaire dans une de vos discussions"),
        (TYPE_WAITING_LOCATION_GROUP, "Préciser la localisation du groupe"),
        (TYPE_GROUP_COORGANIZATION_INVITE, "Invitation à coorganiser un groupe reçue"),
        (TYPE_WAITING_LOCATION_EVENT, "Préciser la localisation d'un événement"),
        (
            TYPE_GROUP_COORGANIZATION_ACCEPTED,
            "Invitation à coorganiser un groupe acceptée",
        ),
        (TYPE_GROUP_INFO_UPDATE, "Mise à jour des informations du groupe"),
        (TYPE_ACCEPTED_INVITATION_MEMBER, "Invitation à rejoindre un groupe acceptée"),
        (TYPE_NEW_ATTENDEE, "Un nouveau participant à votre événement"),
        (TYPE_EVENT_UPDATE, "Mise à jour d'un événement"),
        (TYPE_NEW_EVENT_MYGROUPS, "Votre groupe organise un événement"),
        (TYPE_NEW_REPORT, "Nouveau compte-rendu d'événement"),
        (TYPE_CANCELLED_EVENT, "Événement annulé"),
        (TYPE_REFERRAL, "Personne parrainée"),
        (TYPE_ANNOUNCEMENT, "Associée à une annonce"),
        (
            TYPE_TRANSFERRED_GROUP_MEMBER,
            "Un membre d'un groupe a été transferé vers un autre groupe",
        ),
        (
            TYPE_NEW_MEMBERS_THROUGH_TRANSFER,
            "De nouveaux membres ont été transferés vers le groupe",
        ),
        (TYPE_GROUP_CREATION_CONFIRMATION, "Groupe créé"),
        (TYPE_EVENT_SUGGESTION, "Événement suggéré"),
    )
