import React from "react";

import Notification from "./Notification";
import PropTypes from "prop-types";
import styled from "styled-components";

const Panel = styled.ul`
  width: 430px;
  padding: 0;
  background-color: #fff !important;
  border: 1px solid rgba(0, 0, 0, 0.15);

  @media (min-width: 992px) {
    overflow-y: auto;
    max-height: 60vh;
  }
`;

const Header = styled.li`
  padding: 4px 20px;
  font-weight: bold;
  display: none;

  @media (min-width: 992px) {
    display: list-item;
  }
`;

const NotificationsPanel = ({ notifications }) => {
  return (
    <Panel className="dropdown-menu">
      <Header className="menu-item">Notifications</Header>
      {notifications.length > 0 ? (
        notifications.map(notification => (
          <Notification key={notification.id} {...notification} />
        ))
      ) : (
        <li className="menu-item small">
          <a>Pas de notifications pour le moment</a>
        </li>
      )}
    </Panel>
  );
};

NotificationsPanel.propTypes = {
  notifications: PropTypes.array.isRequired
};

export default NotificationsPanel;
