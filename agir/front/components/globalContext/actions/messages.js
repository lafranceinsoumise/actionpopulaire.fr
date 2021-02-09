import ACTION_TYPE from "@agir/front/globalContext/actionTypes";

import * as api from "@agir/groups/groupPage/api";

export const loadMessages = () => ({
  type: ACTION_TYPE.LOADING_MESSAGES_ACTION,
});

export const refreshingMessages = () => ({
  type: ACTION_TYPE.REFRESHING_MESSAGES_ACTION,
});

export const messagesRefreshed = () => ({
  type: ACTION_TYPE.REFRESHED_MESSAGES_ACTION,
});

export const setMessages = (messages) => (dispatch) => {
  dispatch({
    type: ACTION_TYPE.SET_MESSAGES_ACTION,
    messages,
  });
};

export const setMessage = (message) => (dispatch) => {
  dispatch({
    type: ACTION_TYPE.SET_MESSAGE_ACTION,
    message,
  });
};

export const createMessage = (group, message) => async (dispatch) => {
  dispatch({
    type: ACTION_TYPE.CREATING_MESSAGE_ACTION,
  });
  try {
    const response = await api.createMessage(group.id, message);
    dispatch({
      type: ACTION_TYPE.CREATED_MESSAGE_ACTION,
      error: response.error,
      message: response.data,
    });
  } catch (e) {
    dispatch({
      type: ACTION_TYPE.CREATED_MESSAGE_ACTION,
      error: e.message,
    });
  }
};

export const updateMessage = (message) => async (dispatch) => {
  dispatch({
    type: ACTION_TYPE.UPDATING_MESSAGE_ACTION,
  });
  try {
    const response = await api.updateMessage(message);
    dispatch({
      type: ACTION_TYPE.UPDATED_MESSAGE_ACTION,
      error: response.error,
      message: response.data,
    });
  } catch (e) {
    dispatch({
      type: ACTION_TYPE.UPDATED_MESSAGE_ACTION,
      error: e.message,
    });
  }
};

export const deleteMessage = (message) => async (dispatch) => {
  dispatch({
    type: ACTION_TYPE.DELETING_MESSAGE_ACTION,
  });
  try {
    const response = await api.deleteMessage(message);
    dispatch({
      type: ACTION_TYPE.DELETED_MESSAGE_ACTION,
      error: response.error,
      message,
    });
  } catch (e) {
    dispatch({
      type: ACTION_TYPE.DELETED_MESSAGE_ACTION,
      error: e.message,
    });
  }
};

export const createComment = (comment, message) => async (dispatch) => {
  dispatch({
    type: ACTION_TYPE.CREATING_COMMENT_ACTION,
  });
  try {
    const response = await api.createComment(message.id, comment);
    dispatch({
      type: ACTION_TYPE.CREATED_COMMENT_ACTION,
      error: response.error,
      comment: response.data,
      message,
    });
  } catch (e) {
    dispatch({
      type: ACTION_TYPE.CREATED_COMMENT_ACTION,
      error: e.message,
      message,
    });
  }
};

export const deleteComment = (comment, message) => async (dispatch) => {
  dispatch({
    type: ACTION_TYPE.DELETING_COMMENT_ACTION,
  });
  try {
    const response = await api.deleteComment(comment);
    dispatch({
      type: ACTION_TYPE.DELETED_COMMENT_ACTION,
      error: response.error,
      comment,
      message,
    });
  } catch (e) {
    dispatch({
      type: ACTION_TYPE.DELETED_COMMENT_ACTION,
      error: e.message,
      message,
    });
  }
};
