import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import NotificationSettingItem from "./NotificationSettingItem";

const StyledName = styled.div`
  display: grid;
  grid-template-columns: 1fr auto auto;
  grid-gap: 0 0.5rem;
  align-items: center;

  span {
    font-size: 1rem;
    font-weight: 600;
    line-height: 1.5rem;
  }

  small {
    font-size: 0.688rem;
    line-height: 1;
  }
`;
const StyledGroup = styled.div`
  display: grid;
  grid-template-columns: 100%;
  grid-gap: 1rem 0;

  & + & {
    padding-top: 1.5rem;

    ${StyledName} {
      small {
        display: none;
      }
    }
  }
`;

const NotificationSettingGroup = (props) => {
  const { name, notifications, onChange, disabled } = props;

  if (!Array.isArray(notifications) || notifications.length === 0) {
    return null;
  }

  return (
    <StyledGroup>
      <StyledName>
        <span>{name}</span>
        <small>Notifications</small>
        <small>E-mail</small>
      </StyledName>
      {notifications.map((notification) => (
        <NotificationSettingItem
          key={notification.id}
          notification={notification}
          onChange={onChange}
          disabled={disabled}
        />
      ))}
    </StyledGroup>
  );
};
NotificationSettingGroup.propTypes = {
  name: PropTypes.string,
  notifications: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string.isRequired,
      label: PropTypes.string.isRequired,
      pushNotification: PropTypes.bool,
      email: PropTypes.bool,
    })
  ),
  onChange: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
};
export default NotificationSettingGroup;
