import axios from "@agir/lib/utils/axios";

export const ENDPOINT = {
  login: "/api/connexion/",
  checkCode: "/api/connexion/code/",
  logout: "/api/deconnexion",
};

export const login = async (email) => {
  const result = {
    data: null,
    error: null,
  };
  const url = ENDPOINT.login;
  const body = { email };
  try {
    const response = await axios.post(url, body);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const checkCode = async (code) => {
  const result = {
    data: null,
    error: null,
  };
  const url = ENDPOINT.checkCode;
  const body = { code };
  try {
    const response = await axios.post(url, body);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const logout = async () => {
  const result = {
    data: null,
    error: null,
  };
  const url = ENDPOINT.checkCode;
  try {
    const response = await axios.get(url);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};
