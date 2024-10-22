import axios from "@agir/lib/utils/axios";
import {getDefaultNotifications} from "@agir/notifications/common/notifications.config";

export const ENDPOINT = {
  getSubscriptions: "/api/notifications/subscriptions/",
  createSubscriptions: "/api/notifications/subscriptions/",
  deleteSubscriptions: "/api/notifications/subscriptions/",
};

export const createSubscriptions = async (subscriptions) => {
  const result = {
    success: false,
    error: null,
  };
  const url = ENDPOINT.createSubscriptions;
  try {
    const response = await axios.post(url, subscriptions);
    result.success = response.status === 201;
    result.data = response.data || null;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export const deleteSubscriptions = async (subscriptions) => {
  const result = {
    success: false,
    error: null,
  };
  const url = ENDPOINT.deleteSubscriptions;
  try {
    const response = await axios.delete(url, { data: subscriptions });
    result.success = response.status === 201;
    result.data = response.data || null;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

export async function setupDefaultNotification() {
  /**
   * we must send subscribe for each notification type because if
   * we send as a list, and there is only one which is already registered, the API will trigger a constraint and ignore the other ones.
   */
  const subscriptionRequest = getDefaultNotifications().map((notification) => {
    return notification.activityTypes.map((type) =>
        createSubscriptions([{
          activityType: type,
          type: "push",
        }]));
  });
  await Promise.all(subscriptionRequest.flat(2))
}