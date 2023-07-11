import {
  NEWSLETTER_OPTIONS,
  getNewsletterOptions,
} from "@agir/front/authentication/common";

const PERSON_NOTIFICATIONS = [
  {
    id: "campaign_news",
    type: "Mon compte Action Populaire",
    icon: "rss",
    subtype: "Nouveautés",
    label: "Informations importantes de la campagne",
    hasEmail: false,
    hasPush: true,
    activityTypes: [],
  },
  {
    id: "person_related_news",
    type: "Mon compte Action Populaire",
    icon: "rss",
    subtype: "Nouveautés",
    label: "Nouveautés qui me concernent",
    hasEmail: true,
    hasPush: true,
    activityTypes: ["referral-accepted"],
  },
  {
    id: "security_and_payment_alerts",
    type: "Compte et sécurité",
    icon: "lock",
    subtype: "Compte et sécurité",
    label: "Alertes de sécurité et de paiement",
    hasEmail: false,
    hasPush: false,
    activityTypes: [],
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
    activityTypes: ["event-suggestion"],
  },
  {
    id: "event_updates",
    type: "Événements",
    icon: "calendar",
    subtype: "Événements auxquels je participe",
    label: "Mise à jour d'événement",
    hasEmail: true,
    hasPush: true,
    activityTypes: ["event-update"],
  },
  {
    id: "event_reminders",
    type: "Événements",
    icon: "calendar",
    subtype: "Événements auxquels je participe",
    label: "Rappel d'événement",
    hasEmail: false,
    hasPush: true,
    activityTypes: ["reminder-upcoming-event-start"],
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
    hasEmail: true,
    hasPush: true,
    activityTypes: ["new-attendee"],
  },
  {
    id: "event_group_attendee_notifications",
    type: "Événements",
    icon: "calendar",
    subtype: "Événements que j'organise",
    label: "Nouveaux groupes participants",
    hasEmail: false,
    hasPush: true,
    activityTypes: ["new-group-attendee"],
  },
  {
    id: "event_task_reminders",
    type: "Événements",
    icon: "calendar",
    subtype: "Événements que j'organise",
    label: "Tâches à effectuer ",
    hasEmail: false,
    hasPush: true,
    activityTypes: [
      "waiting-location-event",
      "reminder-docs-event-eve",
      "reminder-docs-event-nextday",
    ],
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
    id: "group_join_event",
    type: "Groupes",
    icon: "users",
    subtype: "Événements",
    label: "Participation à un événement",
    hasEmail: false,
    hasPush: true,
    isActive: (group) => !group.isReferent,
    activityTypes: ["new-event-participation-mygroups"],
  },
  {
    id: "group_event_notifications",
    type: "Groupes",
    icon: "users",
    subtype: "Mises à jour du groupe",
    label: "Nouvel événement du groupe",
    hasEmail: true,
    hasPush: true,
    isActive: true,
    activityTypes: ["new-event-mygroups" /*"group-coorganization-info"*/],
  },
  {
    id: "group_event_report_notifications",
    type: "Groupes",
    icon: "users",
    subtype: "Mises à jour du groupe",
    label: "Compte rendu d'un événement du groupe",
    hasEmail: true,
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
    hasEmail: true,
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
    hasEmail: true,
    hasPush: true,
    isActive: true,
    activityTypes: ["new-message"],
  },
  {
    id: "group_comment_notifications",
    type: "Groupes",
    icon: "users",
    subtype: "Discussions",
    label: "Réponses à toutes les discussions",
    hasEmail: false,
    hasPush: true,
    isActive: true,
    activityTypes: ["new-comment"],
  },
  {
    id: "group_restricted_comment_notifications",
    type: "Groupes",
    icon: "users",
    subtype: "Discussions",
    label: "Réponses aux discussions auxquelles je participe",
    hasEmail: true,
    hasPush: true,
    isActive: true,
    activityTypes: ["new-comment-restricted"],
  },
  {
    id: "group_member_notifications",
    type: "Groupes",
    icon: "users",
    subtype: "Gestion de mon groupe",
    label: "Nouveaux membres",
    hasEmail: true,
    hasPush: true,
    isActive: (group) => group.isManager,
    activityTypes: [
      "new-follower",
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

const getNewsletterNotifications = (user) => {
  if (!user) {
    return [];
  }

  return getNewsletterOptions(user).map((option) => ({
    id: option.value,
    label: option.label,
    active: option.active,
    type: "Lettres d'information",
    icon: "rss",
    subtype: "Newsletter",
    hasEmail: true,
    hasPush: false,
    isNewsletter: true,
  }));
};

export const getAllNotifications = (user) => [
  ...getNewsletterNotifications(user),
  ...PERSON_NOTIFICATIONS,
  ...getGroupNotifications(user?.groups),
];

export const getNewsletterStatus = (newsletters) => {
  if (!newsletters || !Array.isArray(newsletters)) {
    return {};
  }
  let newsletterStatus = {};
  Object.values(NEWSLETTER_OPTIONS).forEach((opt) => {
    if (!opt.value) {
      return;
    }
    newsletterStatus = {
      ...newsletterStatus,
      [opt.value]: { email: newsletters.includes(opt.value) },
    };
  });
  return newsletterStatus;
};

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
