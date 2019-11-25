import { hot } from "react-hot-loader/root"; // doit être importé avant React

import React, { useEffect, useState, useRef } from "react";
import PropTypes from "prop-types";

import useInterval from "./intervalHook";
import NotificationButton from "./NotificationButton";
import NotificationsPanel from "./NotificationsPanel";
import axios from "@agir/lib/utils/axios";

function markAsSeen(notifications) {
  const unreadNotifications = notifications.filter(n => n.status === "U");

  if (unreadNotifications.length > 0) {
    axios.post("/notification/seen/", {
      notifications: notifications.filter(n => n.status === "U").map(n => n.id)
    });
  }

  return notifications.map(n => ({
    ...n,
    status: n.status === "U" ? "S" : n.status
  }));
}

function mergeNotifications(former, updated) {
  const map = new Map();

  for (let notification of former) {
    map.set(notification.id, notification);
  }
  for (let notification of updated) {
    map.set(notification.id, notification);
  }

  const notifications = Array.from(map.values());

  notifications.sort((a, b) => Date.parse(b.created) - Date.parse(a.created));

  return notifications;
}

const NotificationsCenter = ({ notifications: initialNotifications }) => {
  const [notifications, setNotifications] = useState(initialNotifications);
  const [loadingMore, setLoadingMore] = useState("ready");
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  // ajoute gestionnaire d'événements sur l'intégralité du document pour permettre
  // de fermer le menu en cliquant n'importe où ailleurs
  // dans le cas où l'élément a disparu, c'est dû à un update entretemps,
  // il ne faut pas fermer le menu
  useEffect(() => {
    function hideMenu(e) {
      if (
        ref.current &&
        !ref.current.contains(e.target) &&
        document.body.contains(e.target)
      ) {
        setOpen(false);
      }
    }

    document.addEventListener("click", hideMenu);
    return function cleanup() {
      document.removeEventListener("click", hideMenu);
    };
  });

  useInterval(async () => {
    try {
      const res = await axios.get("/notification/liste", {
        length: notifications.length
      });
      setNotifications(mergeNotifications(notifications, res.data));
    } catch (e) {
      // eslint-disable-next-line no-console
      console.log("Impossible de mettre à jours les notifications", e);
    }
  }, 120 * 1000);

  const unread = notifications.filter(
    notification => notification.status === "U"
  ).length;

  const loadMore = async e => {
    e.preventDefault();
    setLoadingMore("loading");
    try {
      const res = await axios.get("/notification/liste", {
        params: {
          offset: notifications.length,
          length: 5
        }
      });
      setNotifications(mergeNotifications(notifications, res.data));

      setLoadingMore(res.data.length === 0 ? "finished" : "ready");
    } catch (e) {
      setLoadingMore("error");
    }
  };

  return (
    <li ref={ref} className={`menu-item dropdown ${open ? "open" : ""}`}>
      <NotificationButton
        unread={unread}
        onClick={() => {
          setOpen(!open);
          setNotifications(markAsSeen(notifications));
        }}
      />
      <NotificationsPanel
        notifications={notifications}
        loadingMore={loadingMore}
        loadMore={loadMore}
      />
    </li>
  );
};

NotificationsCenter.propTypes = {
  notifications: PropTypes.array
};

export default hot(NotificationsCenter);
