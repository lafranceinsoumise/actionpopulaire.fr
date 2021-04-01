import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import Accordion from "@agir/front/genericComponents/Accordion";
import NotificationSettingGroup from "./NotificationSettingGroup";
import Panel, { StyledBackButton } from "@agir/front/genericComponents/Panel";

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
  const { isOpen, close, notifications, onChange, disabled } = props;

  const byType = useMemo(() => {
    const result = {};

    notifications.forEach((notification) => {
      if (!result[notification.type]) {
        result[notification.type] = {};
      }
      if (!result[notification.type][notification.subtype]) {
        result[notification.type][notification.subtype] = [];
      }

      result[notification.type][notification.subtype].push(notification);
    });

    return result;
  }, [notifications]);

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
        <Accordion key={type} name={type} icon="users">
          <AccordionContent>
            {Object.keys(byType[type]).map((subtype) => (
              <NotificationSettingGroup
                key={subtype}
                name={subtype}
                notifications={byType[type][subtype]}
                disabled={disabled}
                onChange={onChange}
              />
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
      pushNotification: PropTypes.bool,
      email: PropTypes.bool,
      type: PropTypes.string,
      subtype: PropTypes.string,
    }).isRequired
  ),
  onChange: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
};
export default NotificationSettingPanel;
