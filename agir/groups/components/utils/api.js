import axios from "@agir/lib/utils/axios";
import querystring from "query-string";

export const ENDPOINT = {
  getGroup: "/api/groupes/:groupPk/",
  getGroupSuggestions: "/api/groupes/:groupPk/suggestions/",

  joinGroup: "/api/groupes/:groupPk/rejoindre/",
  followGroup: "/api/groupes/:groupPk/suivre/",
  updateOwnMembership: "/api/groupes/:groupPk/membre/",
  quitGroup: "/api/groupes/:groupPk/quitter/",

  getUpcomingEvents: "/api/groupes/:groupPk/evenements/a-venir/",
  getPastEvents:
    "/api/groupes/:groupPk/evenements/passes/?page=:page&page_size=:pageSize",
  getPastEventReports: "/api/groupes/:groupPk/evenements/compte-rendus/",

  getEventsJoinedByGroup: "/api/groupes/:groupPk/evenements-rejoints/",

  getMessages: "/api/groupes/:groupPk/messages/?page=:page&page_size=:pageSize",
  getMessage: "/api/groupes/messages/:messagePk/",

  createMessage: "/api/groupes/:groupPk/messages/",
  createPrivateMessage: "/api/groupes/:groupPk/envoi-message-prive/",
  updateMessage: "/api/groupes/messages/:messagePk/",
  deleteMessage: "/api/groupes/messages/:messagePk/",
  messageNotification: "/api/groupes/messages/notification/:messagePk/",
  messageLocked: "/api/groupes/messages/verrouillage/:messagePk/",
  messageParticipants: "/api/groupes/messages/:messagePk/participants/",

  getComments: "/api/groupes/messages/:messagePk/comments/",
  createComment: "/api/groupes/messages/:messagePk/comments/",
  deleteComment: "/api/groupes/messages/comments/:commentPk/",
  setAllMessagesRead: "/api/messages/all-read/",

  getMembers: "/api/groupes/:groupPk/membres/",
  updateGroup: "/api/groupes/:groupPk/update/",
  inviteToGroup: "/api/groupes/:groupPk/invitation/",
  getMemberPersonalInformation: "/api/groupes/membres/:memberPk/informations/",
  updateMember: "/api/groupes/membres/:memberPk/",
  getFinance: "/api/groupes/:groupPk/finance/",

  report: "/api/report/",

  createGroupExternalLink: "/api/groupes/:groupPk/link/",
  groupExternalLink: "/api/groupes/:groupPk/link/:linkPk/",

  searchGroups: "/api/groupes/recherche/",
  geoSearchGroups: "/api/groupes/recherche/geo/",
};

export const getGroupEndpoint = (key, params, querystringParams) => {
  let endpoint = ENDPOINT[key] || "";

  if (params) {
    Object.entries(params).forEach(([key, value]) => {
      endpoint = endpoint.replace(`:${key}`, value);
    });
  }

  if (querystringParams) {
    endpoint += `?${querystring.stringify(querystringParams, {
      arrayFormat: "comma",
    })}`;
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
  const url = getGroupEndpoint("createMessage", { groupPk });
  const body = formatMessage(message);
  try {
    const response = await axios.post(url, body);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const createPrivateMessage = async (groupPk, message) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupEndpoint("createPrivateMessage", { groupPk });
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
  const url = getGroupEndpoint("updateMessage", { messagePk: message.id });
  const body = formatMessage(message);
  try {
    const response = await axios.put(url, body);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const getMessageNotification = async (messagePk) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupEndpoint("messageNotification", {
    messagePk,
  });
  try {
    const response = await axios.get(url);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const updateMessageNotification = async (messagePk, isMuted) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupEndpoint("messageNotification", {
    messagePk,
  });
  try {
    const response = await axios.put(url, { isMuted });
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const updateMessageLock = async (messagePk, isLocked) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupEndpoint("messageLocked", {
    messagePk,
  });
  try {
    const response = await axios.put(url, { isLocked });
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
  const url = getGroupEndpoint("deleteMessage", { messagePk: message.id });
  try {
    const response = await axios.delete(url);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const getMessageParticipants = async (messagePk) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupEndpoint("messageParticipants", { messagePk });
  try {
    const response = await axios.get(url);
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
  const url = getGroupEndpoint("report");
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

export const getComments = async (messagePk) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupEndpoint("getComments", { messagePk });
  try {
    const response = await axios.post(url);
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
  const url = getGroupEndpoint("createComment", { messagePk });
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
  const url = getGroupEndpoint("deleteComment", { commentPk: comment.id });
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
  const url = getGroupEndpoint("report");
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
  const url = getGroupEndpoint("joinGroup", { groupPk });
  try {
    const response = await axios.post(url, {});
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const followGroup = async (groupPk) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupEndpoint("followGroup", { groupPk });
  try {
    const response = await axios.post(url, {});
    result.data = response.data;
  } catch (e) {
    result.error = e?.response?.data || e.message;
  }

  return result;
};

export const quitGroup = async (groupPk) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupEndpoint("quitGroup", { groupPk });
  try {
    const response = await axios.delete(url, {});
    result.data = response.data;
  } catch (e) {
    result.error = e?.response?.data || e.message;
  }

  return result;
};

export const updateGroup = async (groupPk, data) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupEndpoint("updateGroup", { groupPk });
  let headers = undefined;
  let body = data;

  if (body.image) {
    body = new FormData();
    Object.keys(data).forEach((e) => {
      body.append(e, data[e]);
    });
  }

  try {
    const response = await axios.patch(url, body, { headers });
    result.data = response.data;
  } catch (e) {
    if (e.response && e.response.data) {
      result.error =
        e.response.status === 400 && data.image
          ? { image: "La taille du fichier ne doit pas dépasser le 2.5 Mo" }
          : e.response.data;
    } else {
      result.error = e.message;
    }
  }

  return result;
};

export const inviteToGroup = async (groupPk, data) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupEndpoint("inviteToGroup", { groupPk });

  try {
    const response = await axios.post(url, data);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const setAllMessagesRead = async () => {
  const result = {
    data: null,
    error: null,
  };
  try {
    const response = await axios.get(ENDPOINT.setAllMessagesRead);
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
  const url = getGroupEndpoint("getMembers", { groupPk });
  try {
    const response = await axios.get(url);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const getMemberPersonalInformation = async (memberPk) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupEndpoint("getMemberPersonalInformation", {
    memberPk,
  });
  try {
    const response = await axios.get(url);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const updateMember = async (memberPk, data) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupEndpoint("updateMember", { memberPk });

  try {
    const response = await axios.patch(url, data);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const getFinance = async (groupPk) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupEndpoint("getFinance", { groupPk });

  try {
    const response = await axios.get(url);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const createGroupLink = async (groupPk, body) => {
  const result = {
    data: null,
    error: null,
  };

  const url = getGroupEndpoint("createGroupExternalLink", { groupPk });

  try {
    const response = await axios.post(url, body);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const updateGroupLink = async (groupPk, linkPk, body) => {
  const result = {
    data: null,
    error: null,
  };

  const url = getGroupEndpoint("groupExternalLink", {
    groupPk,
    linkPk,
  });

  try {
    const response = await axios.put(url, body);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const saveGroupLink = (groupPk, link) => {
  const body = {
    url: encodeURI(
      link.url.includes("http")
        ? link.url.trim()
        : `https://${link.url.trim()}`,
    ),
    label: link.label,
  };
  return link.id
    ? updateGroupLink(groupPk, link.id, body)
    : createGroupLink(groupPk, body);
};

export const deleteGroupLink = async (groupPk, linkPk) => {
  const result = {
    success: false,
    error: null,
  };

  const url = getGroupEndpoint("groupExternalLink", { groupPk, linkPk });

  try {
    await axios.delete(url);
    result.success = true;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const searchGroups = async (searchTerms, params = {}) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupEndpoint("searchGroups");
  try {
    const response = await axios.get(url, {
      params: { ...params, q: searchTerms },
    });
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || { global: e.message };
  }

  return result;
};

export const updateOwnMembership = async (groupPk, data) => {
  const result = {
    data: null,
    error: null,
  };
  const url = getGroupEndpoint("updateOwnMembership", { groupPk });

  try {
    const response = await axios.patch(url, data);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};
