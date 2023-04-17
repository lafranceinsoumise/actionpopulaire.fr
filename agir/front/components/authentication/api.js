import axios from "@agir/lib/utils/axios";

export const ENDPOINT = {
  login: "/api/connexion/",
  checkCode: "/api/connexion/code/",
  logout: "/api/deconnexion/",
  signUp: "/api/inscription/",
  getProfile: "/api/user/profile/",
  getProfileOptions: "/api/user/profile/",
  updateProfile: "/api/user/profile/",
};

export const getAuthenticationEndpoint = (key, params) => {
  let endpoint = ENDPOINT[key] || "";
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      endpoint = endpoint.replace(`:${key}`, value);
    });
  }
  return endpoint;
};

export const login = async (email) => {
  const result = {
    success: false,
    error: null,
  };
  const url = ENDPOINT.login;
  const body = { email: email.trim() };
  try {
    const response = await axios.post(url, body);
    result.success = response.status === 200;
    result.data = response.data || null;
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
    success: false,
    error: null,
  };
  const url = ENDPOINT.logout;
  try {
    const response = await axios.get(url);
    result.success = response.status === 200;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const signUp = async (data, next) => {
  const result = {
    data: null,
    error: null,
  };
  const formData = {
    email: data.email.trim(),
    location_zip: data.postalCode,
    location_country: data.country,
    next: next || undefined,
  };
  const url = ENDPOINT.signUp;
  try {
    const response = await axios.post(url, formData);
    result.data = response.data;
  } catch (e) {
    result.error = {};
    if (!e.response || !e.response.data) {
      result.error = e.message;
      return result;
    }
    const { email, location_zip, location_country, non_field_errors } =
      e.response.data;
    if (email) {
      result.error.email = email;
    }
    if (location_zip) {
      result.error.postalCode = location_zip;
    }
    if (location_country) {
      result.error.country = location_country;
    }
    if (non_field_errors) {
      result.error.global = non_field_errors;
    }
  }

  return result;
};

export const getProfile = async () => {
  const result = {
    data: null,
    error: null,
  };
  const url = ENDPOINT.getProfile;
  try {
    const response = await axios.get(url);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const getProfileOptions = async () => {
  const result = {
    data: null,
    error: null,
  };
  const url = ENDPOINT.getProfileOptions;
  try {
    const response = await axios.options(url);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const updateProfile = async (body) => {
  const result = {
    data: null,
    error: null,
  };

  const url = ENDPOINT.updateProfile;
  try {
    const response = await axios.patch(url, body);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};
