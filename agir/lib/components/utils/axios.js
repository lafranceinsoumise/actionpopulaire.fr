import axios from "axios";
import Cookies from "js-cookie";

const client = axios.create({
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
});

client.interceptors.request.use(async function (config) {
  if (
    config.url !== "/api/csrf/" &&
    config.method !== "get" &&
    !Cookies.get("csrftoken")
  ) {
    await client.get("/api/csrf/");
  }

  return config;
});

export default client;
