import React from "react";

import Notification from "./Notification";
import PropTypes from "prop-types";

const NotificationsPanel = ({ notifications }) => {
  return (
    <ul className="dropdown-menu">
      {notifications.length > 0 ? (
        notifications.map(notification => (
          <Notification key={notification.id} {...notification} />
        ))
      ) : (
        <li className="menu-item small">
          <a>Pas de notifications pour le moment</a>
        </li>
      )}
    </ul>
  );
};

NotificationsPanel.propTypes = {
  notifications: PropTypes.array.isRequired
};

export default NotificationsPanel;
