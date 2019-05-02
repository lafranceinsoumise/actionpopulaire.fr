import React from "react";
import styled from "styled-components";
import PropTypes from "prop-types";

const NotificationBox = styled.li`
  ${props => (props.status === "C" ? "" : "background-color: #cdf7ff;")}
`;

const NotificationLink = styled.a`
  white-space: normal;
`;

const Notification = ({ id, content, status, link }) => (
  <NotificationBox className="menu-item small" status={status}>
    <NotificationLink
      href={link}
      dangerouslySetInnerHTML={{ __html: content }}
      onClick={e => {
        e.currentTarget.href = `/notification/${id}/`;
      }}
    />
  </NotificationBox>
);
Notification.propTypes = {
  id: PropTypes.number.isRequired,
  content: PropTypes.string.isRequired,
  link: PropTypes.string.isRequired,
  status: PropTypes.string.isRequired
};

export default Notification;
