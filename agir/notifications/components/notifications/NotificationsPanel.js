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

const Action = styled.li`
  text-align: center;
  border-top: 1px solid rgba(0, 0, 0, 0.15);
  color: #888;
`;

const NotificationsPanel = ({ notifications, loadingMore, loadMore }) => {
  return (
    <Panel className="dropdown-menu dropdown-menu-right">
      <Header className="menu-item">Notifications</Header>
      {notifications.length > 0 ? (
        notifications.map((notification) => (
          <Notification key={notification.id} {...notification} />
        ))
      ) : (
        <li className="menu-item small">
          <a>Pas de notifications pour le moment</a>
        </li>
      )}

      <Action>
        {loadingMore === "loading" ? (
          <span>Chargement...</span>
        ) : loadingMore === "ready" ? (
          <a href="#" onClick={loadMore}>
            Charger plus
          </a>
        ) : loadingMore === "error" ? (
          <a href="#" onClick={loadMore}>
            Erreur au chargement...
          </a>
        ) : null}
      </Action>
    </Panel>
  );
};

NotificationsPanel.propTypes = {
  notifications: PropTypes.array.isRequired,
  loadingMore: PropTypes.string,
  loadMore: PropTypes.func,
};

export default NotificationsPanel;
