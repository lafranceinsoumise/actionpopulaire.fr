import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Accordion from "@agir/front/genericComponents/Accordion";
import Button from "@agir/front/genericComponents/Button";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";
import Panel, { StyledBackButton } from "@agir/front/genericComponents/Panel";

import NotificationSettingItem from "./NotificationSettingItem";

const StyledGroupName = styled.div`
  display: grid;
  grid-template-columns: 1fr 70px;
  grid-auto-flow: column;
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
    text-align: right;
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

const StyledDeviceSubscription = styled.div`
  padding: 1rem;
  display: grid;
  grid-template-columns: 1fr auto;
  grid-template-rows: auto auto;
  align-items: center;
  background: ${style.primary100};
  grid-gap: 0 1rem;
  width: calc(100% - 3rem);
  margin: 0 auto 1.5rem;

  h5,
  p {
    font-size: 0.875rem;
    line-height: 1.5;
    margin: 0;
    padding: 0;
  }

  h5 {
    font-weight: 700;
  }

  p {
    font-weight: 400;
  }

  ${Button} {
    grid-column: 2/3;
    grid-row: 1/3;
  }
`;

const StyledUnsupportedSubscription = styled.div`
  padding: 1rem;
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: auto auto;
  background: ${style.black50};
  grid-gap: 1rem;
  width: calc(100% - 3rem);
  margin: 0 auto 1.5rem;

  p {
    font-size: 0.875rem;
    line-height: 1.5;
    margin: 0;
    padding: 0;
    font-weight: 400;
  }
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
    ready,
    subscribeDevice,
    unsubscribeDevice,
    isPushAvailable,
    subscriptionError,
    pushIsReady,
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
      {typeof subscribeDevice === "function" ? (
        <StyledDeviceSubscription>
          <h5>Notifications désactivées</h5>
          <p>Autorisez les notifications sur cet appareil</p>
          {subscriptionError && (
            <p style={{ color: style.redNSP }}>{subscriptionError}</p>
          )}
          <Button color="primary" onClick={subscribeDevice}>
            Activer
          </Button>
        </StyledDeviceSubscription>
      ) : typeof unsubscribeDevice === "function" ? (
        <div style={{ padding: "0 1.5rem 1.5rem" }}>
          <Button color="choose" small onClick={unsubscribeDevice}>
            Désactiver les notifications
          </Button>
        </div>
      ) : pushIsReady && !isPushAvailable ? (
        <StyledUnsupportedSubscription>
          <p>Les notifications ne sont actuellement pas supportées.</p>
        </StyledUnsupportedSubscription>
      ) : null}
      <PageFadeIn ready={ready}>
        {Object.keys(byType).map((type) => (
          <Accordion key={type} name={type} icon={icons[type] || "settings"}>
            <AccordionContent>
              {Object.keys(byType[type]).map((subtype) => (
                <StyledGroup key={subtype}>
                  <StyledGroupName>
                    <span>{subtype}</span>
                    {byType[type][subtype].some(
                      (notificationId) => byId[notificationId].hasPush !== false
                    ) && <small>Notifications</small>}
                    {byType[type][subtype].some(
                      (notificationId) =>
                        byId[notificationId].hasEmail !== false
                    ) && <small>E-mail</small>}
                  </StyledGroupName>
                  {byType[type][subtype].map((notificationId) => (
                    <NotificationSettingItem
                      key={notificationId}
                      notification={byId[notificationId]}
                      onChange={onChange}
                      disabled={disabled}
                      email={
                        activeNotifications[notificationId]?.email || false
                      }
                      push={activeNotifications[notificationId]?.push || false}
                    />
                  ))}
                </StyledGroup>
              ))}
            </AccordionContent>
          </Accordion>
        ))}
      </PageFadeIn>
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
  subscribeDevice: PropTypes.func,
  unsubscribeDevice: PropTypes.func,
  disabled: PropTypes.bool,
  ready: PropTypes.bool,
  isPushAvailable: PropTypes.bool,
  pushIsReady: PropTypes.bool,
  subscriptionError: PropTypes.string,
};
export default NotificationSettingPanel;
