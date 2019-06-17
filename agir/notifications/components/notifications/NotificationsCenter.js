import React, { useEffect, useState, useRef } from "react";
import PropTypes from "prop-types";
import { hot } from "react-hot-loader";

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

const NotificationsCenter = ({ notifications: initialNotifications }) => {
  const [notifications, setNotifications] = useState(initialNotifications);
  const [open, setOpen] = useState(false);
  const ref = useRef(null);

  // ajoute gestionnaire d'événements sur l'intégralité du document pour permettre
  // de fermer le menu en cliquant n'importe où ailleurs
  useEffect(() => {
    function hideMenu(e) {
      if (ref.current && !ref.current.contains(e.target)) {
        setOpen(false);
      }
    }
    document.addEventListener("click", hideMenu);
    return function cleanup() {
      document.removeEventListener("click", hideMenu);
    };
  });

  const unread = notifications.filter(
    notification => notification.status === "U"
  ).length;

  return (
    <li ref={ref} className={`menu-item dropdown ${open ? "open" : ""}`}>
      <NotificationButton
        unread={unread}
        onClick={() => {
          setOpen(!open);
          setNotifications(markAsSeen(notifications));
        }}
      />
      <NotificationsPanel notifications={notifications} />
    </li>
  );
};

NotificationsCenter.propTypes = {
  notifications: PropTypes.array
};

export default hot(module)(NotificationsCenter);
