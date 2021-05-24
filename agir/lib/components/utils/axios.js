import axios from "axios";
import Cookies from "js-cookie";

const client = axios.create({
  xsrfCookieName: "csrftoken",
  xsrfHeaderName: "X-CSRFToken",
});

let CSRFPromise = null;

function updateCSRF() {
  if (CSRFPromise) {
    return CSRFPromise;
  }

  CSRFPromise = client.get("/api/csrf/");
  return CSRFPromise;
}

client.interceptors.request.use(async function (config) {
  if (
    !Cookies.get("csrftoken") &&
    config.url !== "/api/csrf/" &&
    config.method !== "get"
  ) {
    await updateCSRF();
  }

  return config;
});

export default client;
