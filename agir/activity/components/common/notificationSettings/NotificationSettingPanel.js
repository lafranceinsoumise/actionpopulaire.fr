import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import Accordion from "@agir/front/genericComponents/Accordion";
import NotificationSettingItem from "./NotificationSettingItem";
import Panel, { StyledBackButton } from "@agir/front/genericComponents/Panel";

const StyledGroupName = styled.div`
  display: grid;
  grid-template-columns: 1fr 70px auto;
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

    ${StyledGroupName} {
      small {
        display: none;
      }
    }
  }
`;

const AccordionContent = styled.div`
  padding: 1.5rem;
`;

const StyledPanel = styled(Panel)`
  padding-left: 0;
  padding-right: 0;

  ${StyledBackButton} {
    margin-left: 1.5rem;
    padding-bottom: 0;
  }
`;

const NotificationSettingPanel = (props) => {
  const {
    isOpen,
    close,
    notifications,
    activeNotifications,
    onChange,
    disabled,
  } = props;

  const [byType, icons] = useMemo(() => {
    const result = {};
    const icons = {};
    notifications.forEach((notification) => {
      icons[notification.type] = notification.icon;
      if (!result[notification.type]) {
        result[notification.type] = {};
      }
      if (!result[notification.type][notification.subtype]) {
        result[notification.type][notification.subtype] = [];
      }

      result[notification.type][notification.subtype].push(notification.id);
    });

    return [result, icons];
  }, [notifications]);

  const byId = useMemo(
    () =>
      notifications.reduce(
        (byId, notification) => ({ ...byId, [notification.id]: notification }),
        {}
      ),
    [notifications]
  );

  return (
    <StyledPanel shouldShow={isOpen} onClose={close} onBack={close} noScroll>
      <h3
        style={{
          fontSize: "1.25rem",
          fontWeight: 700,
          padding: "0 1.5rem 0.5rem",
        }}
      >
        Notifications
      </h3>
      {Object.keys(byType).map((type) => (
        <Accordion key={type} name={type} icon={icons[type] || "settings"}>
          <AccordionContent>
            {Object.keys(byType[type]).map((subtype) => (
              <StyledGroup key={subtype}>
                <StyledGroupName>
                  <span>{subtype}</span>
                  <small>Notifications</small>
                  <small>E-mail</small>
                </StyledGroupName>
                {byType[type][subtype].map((notificationId) => (
                  <NotificationSettingItem
                    key={notificationId}
                    notification={byId[notificationId]}
                    onChange={onChange}
                    disabled={disabled}
                    email={activeNotifications[notificationId]?.email}
                    push={activeNotifications[notificationId]?.push}
                  />
                ))}
              </StyledGroup>
            ))}
          </AccordionContent>
        </Accordion>
      ))}
    </StyledPanel>
  );
};
NotificationSettingPanel.propTypes = {
  isOpen: PropTypes.bool,
  close: PropTypes.func,
  notifications: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.oneOfType([PropTypes.number, PropTypes.string]).isRequired,
      label: PropTypes.string.isRequired,
      push: PropTypes.bool,
      email: PropTypes.bool,
      type: PropTypes.string,
      subtype: PropTypes.string,
      icon: PropTypes.string,
    }).isRequired
  ),
  activeNotifications: PropTypes.object,
  onChange: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
};
export default NotificationSettingPanel;
