const PERSON_NOTIFICATIONS = [
  {
    id: "campaign_news",
    type: "Nouveautés",
    icon: "rss",
    subtype: "Nouveautés",
    label: "Informations importantes de la campagne",
    hasEmail: false,
    hasPush: true,
    activityTypes: [
      "referral-accepted",
      "transferred-group-member",
      "group-invitation",
    ],
  },
  {
    id: "person_related_news",
    type: "Nouveautés",
    icon: "rss",
    subtype: "Nouveautés",
    label: "Nouveautés qui me concernent",
    hasEmail: false,
    hasPush: true,
    activityTypes: [],
  },

  {
    id: "security_and_payment_alerts",
    type: "Compte et sécurité",
    icon: "lock",
    subtype: "Compte et sécurité",
    label: "Alertes de sécurité et de paiement",
    hasEmail: false,
    hasPush: true,
    activityTypes: ["waiting-payment"],
  },
  {
    id: "donation_reminders",
    type: "Compte et sécurité",
    icon: "lock",
    subtype: "Compte et sécurité",
    label: "Rappels de don",
    hasEmail: false,
    hasPush: true,
    activityTypes: [],
  },
  {
    id: "person_task_reminders",
    type: "Compte et sécurité",
    icon: "lock",
    subtype: "Mes tâches à faire",
    label: "Me rappeler mes tâches à faire régulièrement",
    hasEmail: false,
    hasPush: true,
    activityTypes: [],
  },

  {
    id: "event_suggestions",
    type: "Événements",
    icon: "calendar",
    subtype: "Suggestions",
    label: "Suggestion d'événement",
    hasEmail: false,
    hasPush: true,
    activityTypes: ["new-event-aroundme"],
  },
  {
    id: "event_updates",
    type: "Événements",
    icon: "calendar",
    subtype: "Événements auxquels je participe",
    label: "Mise à jour d'événement",
    hasEmail: false,
    hasPush: true,
    activityTypes: ["event-update", "cancelled-event"],
  },
  {
    id: "event_reminders",
    type: "Événements",
    icon: "calendar",
    subtype: "Événements auxquels je participe",
    label: "Rappel d'événement la veille",
    hasEmail: false,
    hasPush: true,
    activityTypes: [],
  },
  {
    id: "online_event_reminders",
    type: "Événements",
    icon: "calendar",
    subtype: "Événements auxquels je participe",
    label: "Lien de connexion à la visio-conférence 5mn avant",
    hasEmail: false,
    hasPush: true,
    activityTypes: [],
  },
  {
    id: "event_rsvp_notifications",
    type: "Événements",
    icon: "calendar",
    subtype: "Événements que j'organise",
    label: "Nouveaux participant·es",
    hasEmail: false,
    hasPush: true,
    activityTypes: ["new-attendee"],
  },
  {
    id: "event_task_reminders",
    type: "Événements",
    icon: "calendar",
    subtype: "Événements que j'organise",
    label: "Tâches à effectuer ",
    hasEmail: false,
    hasPush: true,
    activityTypes: ["waiting-location-event"],
  },
  {
    id: "event_organizer_updates",
    type: "Événements",
    icon: "calendar",
    subtype: "Événements que j'organise",
    label: "Mises à jour pour les organisateur·ices",
    hasEmail: false,
    hasPush: true,
    activityTypes: [],
  },
].filter((notification) => notification.activityTypes.length > 0);

const GROUP_NOTIFICATIONS = [
  {
    id: "group_event_notifications",
    type: "Groupes",
    icon: "users",
    subtype: "Mises à jour du groupe",
    label: "Nouvel événement du groupe",
    hasEmail: false,
    hasPush: true,
    isActive: true,
    activityTypes: ["new-event-mygroups" /*"group-coorganization-info"*/],
  },
  {
    id: "group_event_report_notifications",
    type: "Groupes",
    icon: "users",
    subtype: "Mises à jour du groupe",
    label: "Compte-rendu d'un événement du groupe",
    hasEmail: false,
    hasPush: true,
    isActive: true,
    activityTypes: ["new-report"],
  },
  {
    id: "group_updates",
    type: "Groupes",
    icon: "users",
    subtype: "Mises à jour du groupe",
    label: "Mise à jour du groupe",
    hasEmail: false,
    hasPush: true,
    isActive: true,
    activityTypes: ["group-info-update"],
  },
  {
    id: "group_message_notifications",
    type: "Groupes",
    icon: "users",
    subtype: "Discussions",
    label: "Nouvelle discussion",
    hasEmail: false,
    hasPush: true,
    isActive: true,
    activityTypes: ["new-message"],
  },
  {
    id: "group_comment_notifications",
    type: "Groupes",
    icon: "users",
    subtype: "Discussions",
    label: "Message d'une discussion à laquelle je participe",
    hasEmail: false,
    hasPush: true,
    isActive: true,
    activityTypes: ["new-comment"],
  },
  {
    id: "group_member_notifications",
    type: "Groupes",
    icon: "users",
    subtype: "Gestion de mon groupe",
    label: "Nouveaux membres",
    hasEmail: false,
    hasPush: true,
    isActive: (group) => group.isManager,
    activityTypes: [
      "new-member",
      "accepted-invitation-member",
      "group-membership-limit-reminder",
      "new-members-through-transfer",
    ],
  },
  {
    id: "group_task_reminders",
    type: "Groupes",
    icon: "users",
    subtype: "Gestion de mon groupe",
    label: "Actions à faire",
    hasEmail: false,
    hasPush: true,
    isActive: (group) => group.isManager,
    activityTypes: ["waiting-location-group", "group-coorganization-invite"],
  },
  {
    id: "group_manager_updates",
    type: "Groupes",
    icon: "users",
    subtype: "Gestion de mon groupe",
    label: "Mises à jour pour les gestionnaires",
    hasEmail: false,
    hasPush: true,
    isActive: (group) => group.isManager,
    activityTypes: [
      "group-creation-confirmation",
      "group-coorganization-accepted",
    ],
  },
].filter((notification) => notification.activityTypes.length > 0);

const getNotificationId = (notificationId, groupId) => {
  if (groupId) {
    return `${notificationId}__${groupId}`;
  }
  return notificationId;
};

const getSingleGroupNotifications = (group) =>
  GROUP_NOTIFICATIONS.filter((notification) => {
    if (typeof notification.isActive === "function") {
      return notification.isActive(group);
    }
    return notification.isActive;
  }).map((notification) => ({
    ...notification,
    id: getNotificationId(notification.id, group.id),
    type: group.name,
    group: group.id,
  }));

const getGroupNotifications = (groups = []) =>
  groups.reduce(
    (arr, group) => [...arr, ...getSingleGroupNotifications(group)],
    []
  );

export const getAllNotifications = (groups = []) => [
  ...PERSON_NOTIFICATIONS,
  ...getGroupNotifications(groups),
];

export const getNotificationStatus = (activeNotifications) => {
  const active = {};

  if (!Array.isArray(activeNotifications) || activeNotifications.length === 0) {
    return active;
  }

  activeNotifications.forEach((activeNotification) => {
    let notificationId = null;
    const notification = activeNotification.group
      ? GROUP_NOTIFICATIONS.find((groupNotification) =>
          groupNotification.activityTypes.includes(
            activeNotification.activityType
          )
        )
      : PERSON_NOTIFICATIONS.find((notification) =>
          notification.activityTypes.includes(activeNotification.activityType)
        );
    if (!notification) {
      return;
    }
    notificationId = getNotificationId(
      notification.id,
      activeNotification.group
    );
    active[notificationId] = active[notificationId] || {
      email: false,
      push: false,
    };
    active[notificationId][activeNotification.type] =
      active[notificationId][activeNotification.type] || [];
    active[notificationId][activeNotification.type].push(activeNotification.id);
  });
  return active;
};
