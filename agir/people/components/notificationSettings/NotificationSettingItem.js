import PropTypes from "prop-types";
import React, { useCallback } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledButton = styled.button`
  outline: none;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 2.25rem;
  height: 2.25rem;
  border-radius: 4px;
  cursor: pointer;
  border: 1px solid;
  background-color: ${({ $active }) =>
    $active ? style.green200 : "transparent"};
  color: ${({ $active }) => ($active ? style.black1000 : style.black500)};
  border-color: ${({ $active }) => ($active ? style.green200 : style.black100)};
  visibility: ${({ $hidden }) => ($hidden ? "hidden" : "visible")};
  transition: all 200ms ease-in-out;

  &:focus {
    outline: none;
    box-shadow: ${({ $disabled }) =>
      !$disabled ? `0 0 0 4px ${style.black100}` : "none"};
  }

  &[disabled] {
    opacity: 0.5;

    &:focus {
      box-shadow: none;
    }
  }
`;
const StyledItem = styled.div`
  display: grid;
  grid-template-columns: 1fr auto auto;
  grid-gap: 0 0.5rem;
  align-items: start;
  font-size: 0.875rem;
  line-height: 1.5;
`;

const NotificationSettingItem = (props) => {
  const { notification, onChange, disabled } = props;

  const togglePush = useCallback(() => {
    onChange({
      ...notification,
      pushNotification: !notification.pushNotification,
    });
  }, [notification, onChange]);

  const toggleEmail = useCallback(() => {
    onChange({
      ...notification,
      email: !notification.email,
    });
  }, [notification, onChange]);

  return (
    <StyledItem>
      <span>{notification.label}</span>
      <StyledButton
        $active={notification.pushNotification}
        $hidden={typeof notification.pushNotification === "undefined"}
        aria-label={`Notifications:${notification.pushNotification} ? "active" : "inactive"}`}
        onClick={togglePush}
        disabled={disabled}
      >
        <RawFeatherIcon width="1.25rem" height="1.25rem" name="bell" />
      </StyledButton>
      <StyledButton
        $active={notification.email}
        $hidden={typeof notification.email === "undefined"}
        aria-label={`Notifications:${notification.email} ? "active" : "inactive"}`}
        onClick={toggleEmail}
        disabled={disabled}
      >
        <RawFeatherIcon width="1.25rem" height="1.25rem" name="mail" />
      </StyledButton>
    </StyledItem>
  );
};
NotificationSettingItem.propTypes = {
  notification: PropTypes.shape({
    label: PropTypes.string.isRequired,
    pushNotification: PropTypes.bool,
    email: PropTypes.bool,
  }).isRequired,
  onChange: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
};
export default NotificationSettingItem;
