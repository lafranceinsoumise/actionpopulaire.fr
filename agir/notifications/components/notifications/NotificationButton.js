import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";

const UnreadCounter = styled.span`
  @media (min-width: 992px) {
    position: absolute;
    top: 12px;
    right: 2px;
  }
`;

const NotificationTitle = styled.span`
  @media (min-width: 992px) {
    display: none;
  }
`;

const NotificationIcon = styled.i`
  display: none;
  @media (min-width: 992px) {
    display: inline-block;
  }
`;

const NotificationButton = ({ unread, onClick }) => (
  <a
    onClick={e => {
      onClick(e);
      e.preventDefault();
    }}
    href="#"
  >
    <NotificationIcon className="fa fa-comment" />
    <NotificationTitle>Notifications</NotificationTitle>{" "}
    {unread > 0 && <UnreadCounter className="badge">{unread}</UnreadCounter>}
  </a>
);
NotificationButton.propTypes = {
  unread: PropTypes.number,
  onClick: PropTypes.func
};

export default NotificationButton;
