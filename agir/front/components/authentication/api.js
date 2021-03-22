import axios from "@agir/lib/utils/axios";

export const ENDPOINT = {
  login: "/api/connexion/",
  checkCode: "/api/connexion/code/",
  logout: "/api/deconnexion",
  signUp: "/api/people/subscription/",
  getProfile: "/api/user/profile/",
  getProfileOptions: "/api/user/profile/",
  updateProfile: "/api/user/profile/",
};

export const login = async (email) => {
  const result = {
    success: false,
    error: null,
  };
  const url = ENDPOINT.login;
  const body = { email };
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
  const url = ENDPOINT.checkCode;
  try {
    const response = await axios.get(url);
    result.success = response.status === 200;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const signUp = async (data) => {
  const result = {
    data: null,
    error: null,
  };
  const formData = {
    email: data.email,
    location_zip: data.postalCode,
  };
  const url = ENDPOINT.signUp;
  try {
    const response = await axios.post(url, formData);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
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

export const updateProfile = async (data) => {
  const result = {
    data: null,
    error: null,
  };

  let formData = {};

  if (data.reasonChecked) {
    formData = {
      ...formData,
      is2022: data.reasonChecked === 0 || null,
      isInsoumise: data.reasonChecked === 1 || null,
    };
  }

  if (data.displayName) {
    formData = {
      ...formData,
      displayName: data.displayName,
      firstName: data.firstName || "",
      lastName: data.lastName || "",
      contactPhone: data.phone || "",
      mandat: data.mandat || [],
    };
  }

  const url = ENDPOINT.updateProfile;
  try {
    const response = await axios.patch(url, formData);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};
