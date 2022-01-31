const config = [
  "/api/session/",
  "/api/2022/dons/",

  "/api/user/activities/",
  "/api/user/messages/",
  "/api/user/messages/unread_count/",
  "/api/user/messages/recipients/",
  "/api/notifications/subscriptions/",

  "/api/evenements/rsvped/",
  "/api/evenements/rsvped/passes/",
  "/api/evenements/rsvped/en-cours/",
  "/api/evenements/suggestions/",
  "/api/evenements/mes-groupes/",
  "/api/evenements/organises/",
  new RegExp(".+/api/evenements/[0-9a-f-]+/$"),
  new RegExp(".+/api/evenements/[0-9a-f-]+/details/$"),

  "/api/groupes/",
  new RegExp("/api/groupes/[0-9a-f-]+/$"),
  new RegExp("/api/groupes/[0-9a-f-]+/suggestions/$"),
  new RegExp("/api/groupes/[0-9a-f-]+/evenements/a-venir/$"),
  new RegExp("/api/groupes/[0-9a-f-]+/evenements/passes/$"),
  new RegExp("/api/groupes/[0-9a-f-]+/messages/$"),
];

export default config;
