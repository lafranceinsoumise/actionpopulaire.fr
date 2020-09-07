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

const NotificationButton = ({ unread, onClick }) => (
  <a
    onClick={(e) => {
      onClick(e);
      e.preventDefault();
    }}
    href="#"
    className="dropdown-toggle"
    data-toggle="dropdown"
  >
    <i className="fa fa-comment" />
    {unread > 0 && <UnreadCounter className="badge">{unread}</UnreadCounter>}
  </a>
);
NotificationButton.propTypes = {
  unread: PropTypes.number,
  onClick: PropTypes.func,
};

export default NotificationButton;
