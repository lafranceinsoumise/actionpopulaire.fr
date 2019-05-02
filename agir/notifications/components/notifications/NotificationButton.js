import React from "react";
import PropTypes from "prop-types";

const NotificationButton = ({ unread, onClick }) => (
  <a
    onClick={e => {
      onClick(e);
      e.preventDefault();
    }}
    href="#"
  >
    <i className="fa fa-comment" />{" "}
    {unread > 0 && <span className="badge">{unread}</span>}
  </a>
);
NotificationButton.propTypes = {
  unread: PropTypes.number,
  onClick: PropTypes.func
};

export default NotificationButton;
