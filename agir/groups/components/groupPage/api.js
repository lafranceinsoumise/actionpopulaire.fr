import axios from "@agir/lib/utils/axios";

export const ENDPOINT = {
  getGroup: "/api/groupes/:groupPk/",
  getGroupSuggestions: "/api/groupes/:groupPk/suggestions/",
  joinGroup: "/api/groupes/:groupPk/rejoindre/",

  getUpcomingEvents: "/api/groupes/:groupPk/evenements/a-venir/",
  getPastEvents:
    "/api/groupes/:groupPk/evenements/passes/?page=:page&page_size=:pageSize",
  getPastEventReports: "/api/groupes/:groupPk/evenements/compte-rendus/",

  getMessages: "/api/groupes/:groupPk/messages/?page=:page&page_size=:pageSize",
  getMessage: "/api/groupes/messages/:messagePk/",

  createMessage: "/api/groupes/:groupPk/messages/",
  updateMessage: "/api/groupes/messages/:messagePk/",
  deleteMessage: "/api/groupes/messages/:messagePk/",

  getComments: "/api/groupes/messages/:messagePk/comments/",
  createComment: "/api/groupes/messages/:messagePk/comments/",
  deleteComment: "/api/groupes/messages/comments/:commentPk/",

  getMembers: "/api/groupes/:groupPk/members/",
  updateGroup: "/api/groupes/:groupPk/general/",

  report: "/api/report/",
};

export const getGroupPageEndpoint = (key, params) => {
  let endpoint = ENDPOINT[key] || "";
  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      endpoint = endpoint.replace(`:${key}`, value);
    });
  }
  return endpoint;
};

export const formatMessage = (message) => ({
  ...message,
  linkedEvent: (message.linkedEvent && message.linkedEvent.id) || null,
});

export const createMessage = async (groupPk, message) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupPageEndpoint("createMessage", { groupPk });
  const body = formatMessage(message);
  try {
    const response = await axios.post(url, body);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const updateMessage = async (message) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupPageEndpoint("updateMessage", { messagePk: message.id });
  const body = formatMessage(message);
  try {
    const response = await axios.put(url, body);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const deleteMessage = async (message) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupPageEndpoint("deleteMessage", { messagePk: message.id });
  try {
    const response = await axios.delete(url);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const reportMessage = async (message) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupPageEndpoint("report");
  const body = {
    object_id: message.id,
    content_type: "msgs.supportgroupmessage",
  };
  try {
    const response = await axios.post(url, body);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const createComment = async (messagePk, comment) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupPageEndpoint("createComment", { messagePk });
  const body = {
    text: comment,
  };
  try {
    const response = await axios.post(url, body);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const deleteComment = async (comment) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupPageEndpoint("deleteComment", { commentPk: comment.id });
  try {
    const response = await axios.delete(url);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const reportComment = async (comment) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupPageEndpoint("report");
  const body = {
    object_id: comment.id,
    content_type: "msgs.supportgroupmessagecomment",
  };
  try {
    const response = await axios.post(url, body);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const joinGroup = async (groupPk) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupPageEndpoint("joinGroup", { groupPk });
  try {
    const response = await axios.post(url, {});
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const getMembers = async (groupPk) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupPageEndpoint("getMembers", { groupPk });
  try {
    const response = await axios.get(url);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const updateGroup = async (groupPk, data) => {
  console.log("Update group : ", groupPk, data);
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupPageEndpoint("updateGroup", { groupPk });
  try {
    const response = await axios.post(url, data);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};
