const config = [
  "/api/session/",
  "/api/evenements/rsvped/",
  "/api/evenements/suggestions/",
  "/api/groupes/",
  "/api/user/activities/",
  new RegExp(".+/api/evenements/[0-9a-f-]+/$"),
];

export default config;
