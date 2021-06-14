import { routeConfig } from "@agir/front/app/routes.config";

const ACTIVITY_CONFIG = {
  announcement: {
    icon: "bell",
  },
  "group-coorganization-accepted": {
    icon: "calendar",
    hasEvent: true,
  },
  "group-info-update": {
    icon: "info",
  },
  "accepted-invitation-member": {
    icon: "user-plus",
  },
  "new-attendee": {
    icon: "user-plus",
  },
  "event-update": {
    icon: "info",
    hasEvent: true,
  },
  "new-event-mygroups": {
    icon: "calendar",
    hasEvent: true,
  },
  "new-report": {
    icon: "file-text",
    hasEvent: true,
  },
  "event-suggestion": {
    icon: "calendar",
    hasEvent: true,
  },
  "group-coorganization-info": {
    icon: "calendar",
    hasEvent: true,
  },
  "cancelled-event": {
    icon: "x-circle",
  },
  "referral-accepted": {
    icon: "share-2",
  },
  "transferred-group-member": {
    icon: "info",
  },
  "new-members-through-transfer": {
    icon: "user-plus",
  },
  "group-membership-limit-reminder": {
    icon: "info",
    action: ({ meta, supportGroup, routes }) => {
      const { membershipLimitNotificationStep } = meta;

      if (membershipLimitNotificationStep <= 2) {
        return supportGroup?.routes?.membershipTransfer
          ? {
              href: supportGroup.routes.membershipTransfer,
              label: "Diviser mon équipe",
            }
          : null;
      }

      return routes?.groupTransferHelp
        ? {
            href: routes?.groupTransferHelp,
            label: "Diviser mon équipe",
          }
        : null;
    },
  },
  "waiting-payment": {
    icon: "alert-circle",
    action: ({ event }) =>
      event?.routes?.rsvp
        ? {
            href: event.routes.rsvp,
            label: "Payer",
          }
        : null,
  },
  "group-invitation": {
    icon: "mail",
    action: ({ supportGroup }) =>
      supportGroup?.id
        ? {
            to: routeConfig.groupDetails.getLink({
              groupPk: supportGroup.id,
            }),
            label: "Rejoindre",
          }
        : null,
  },
  "new-member": {
    icon: "user-plus",
    action: ({ supportGroup }) =>
      supportGroup?.id
        ? {
            to: routeConfig.groupSettings.getLink({
              groupPk: supportGroup.id,
              activePanel: "membres",
            }),
            label: "Voir les membres",
          }
        : null,
  },
  "waiting-location-group": {
    icon: "alert-circle",
    action: ({ supportGroup }) =>
      supportGroup.id
        ? {
            to: routeConfig.groupDetails.getLink({ groupPk: supportGroup.id }),
            label: "Mettre à jour",
          }
        : null,
  },
  "group-coorganization-invite": {
    icon: "mail",
    action: ({ event }) =>
      event?.id
        ? {
            to: routeConfig.eventDetails.getLink({ eventPk: event.id }),
            label: "Voir",
          }
        : null,
  },
  "waiting-location-event": {
    icon: "alert-circle",
    action: ({ event }) =>
      event?.routes?.manage
        ? {
            href: event.routes.manage,
            label: "Mettre à jour",
          }
        : null,
  },
  "group-creation-confirmation": {
    icon: "users",
    action: ({ routes }) =>
      routes?.newGroupHelp
        ? {
            href: routes.newGroupHelp,
            label: "Lire l'article",
          }
        : null,
  },
};

export default ACTIVITY_CONFIG;
