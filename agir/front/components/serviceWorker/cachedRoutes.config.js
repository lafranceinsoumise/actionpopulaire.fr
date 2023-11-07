const config = [
  "/api/session/",
  "/api/2022/dons/",

  "/api/user/activities/",
  "/api/user/messages/",
  "/api/user/messages/unread_count/",
  "/api/user/messages/recipients/",
  "/api/notifications/subscriptions/",

  "/api/elections/circonscription-legislatives/",

  "/api/evenements/options/",
  "/api/evenements/rsvped/",
  "/api/evenements/rsvped/passes/",
  "/api/evenements/rsvped/en-cours/",
  "/api/evenements/suggestions/",
  "/api/evenements/mes-groupes/",
  "/api/evenements/organises/",
  "/api/evenements/grands-evenements/",

  new RegExp(".+/api/evenements/[0-9a-f-]+/$"),
  new RegExp(".+/api/evenements/[0-9a-f-]+/details/$"),

  "/api/groupes/",
  "/api/groupes/suggestions/",
  "/api/groupes/thematiques/",
  new RegExp("/api/groupes/[0-9a-f-]+/$"),
  new RegExp("/api/groupes/[0-9a-f-]+/suggestions/$"),
  new RegExp("/api/groupes/[0-9a-f-]+/evenements/a-venir/$"),
  new RegExp("/api/groupes/[0-9a-f-]+/evenements/passes/$"),
  new RegExp("/api/groupes/[0-9a-f-]+/messages/$"),

  new RegExp("/api/announcement/custom/.+/$"),
];

export default config;
