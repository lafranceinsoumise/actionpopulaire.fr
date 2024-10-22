import { useCallback, useEffect, useMemo, useState } from "react";

import axios from "@agir/lib/utils/axios";
import logger from "@agir/lib/utils/logger";
const log = logger(__filename);

/**
 * On utilise GCM pour gérer les appareils Android et iOS via Firebase.
 * @type {{WEBPUSH: string, ANDROID: string, IOS: string}}
 */
export const DEVICE_TYPE = {
  ANDROID: "gcm",
  IOS: "gcm",
  WEBPUSH: "webpush",
};

export const getSubscription = async (deviceType, token) => {
  try {
    const deviceSubscription = await axios.get(
      `/api/device/${deviceType}/${token}/`,
    );
    log.debug(
      `${deviceType}: Retrieved push subscription for token ${token}`,
      deviceSubscription.data.active,
    );
    return deviceSubscription.data.active;
  } catch (err) {
    log.error(
      `${deviceType}: Error while retrieving push subscription for token ${token}`,
      err,
    );
    return err.response?.status === 404 ? undefined : false;
  }
};

export const subscribe = async (deviceType, token) => {
  try {
    await axios.post(`/api/device/${deviceType}/`, {
      name: "Action populaire",
      registration_id: token,
      cloud_message_type:
        deviceType === DEVICE_TYPE.ANDROID ? "FCM" : undefined,
      active: true,
    });
    log.debug(`${deviceType}: Created push subscription for token ${token}`);
    return true;
  } catch (err) {
    log.error(
      `${deviceType}: Error while creating push subscription for token ${token}`,
      err,
    );
    return false;
  }
};

export const unsubscribe = async (deviceType, token) => {
  try {
    await axios.put(`/api/device/${deviceType}/${token}/`, {
      registration_id: token,
      active: false,
    });
    log.debug(`${deviceType}: Disabled push subscription for token ${token}`);
    return true;
  } catch (err) {
    log.error(
      `${deviceType}: Error while disabling push subscription for token ${token}`,
      err,
    );
    return err.response?.status === 404;
  }
};
