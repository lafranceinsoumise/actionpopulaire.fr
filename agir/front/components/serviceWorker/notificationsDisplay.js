import axios from "@agir/lib/utils/axios";

const doDisplayNotification = async function (message) {
  if (message.startsWith("activity:")) {
    let res = await axios.get(
      `/api/activity/${message.replace("activity:", "")}`
    );

    // TODO: display right notification based on activity data

    return self.registration.showNotification("NOTIFICATION TITLE", {
      body: "Activity notification",
      timestamp: Date.parse(res.data.timestamp),
    });
  }

  return self.registration.showNotification("NOTIFICATION TITLE", {
    body: message,
  });
};

self.addEventListener("push", function (event) {
  const message = event.data.text();

  /* callback for push event must be synced, and event must be attached
     to a promise if no notification has been displayed when promise returns,
     the broswer issues an (ugly) warning that data has been sent in background
   */
  event.waitUntil(doDisplayNotification(message));
});
