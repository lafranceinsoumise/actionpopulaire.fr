import axios from "axios";

const client = axios.create({
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
});

client.interceptors.request.use(async function (config) {
  if (config.url !== "/api/csrf/" && config.method !== "get") {
    await client.get("/api/csrf/");
  }

  return config;
});

export default client;
