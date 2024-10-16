import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import Accordion from "@agir/front/genericComponents/Accordion";
import Button from "@agir/front/genericComponents/Button";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";
import Panel, { StyledBackButton } from "@agir/front/genericComponents/Panel";
import Link from "@agir/front/app/Link";

import NotificationSettingItem from "./NotificationSettingItem";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";

import { useMobileApp } from "@agir/front/app/hooks";
import { usePush } from "@agir/notifications/push/subscriptions";
import NotificationGrantedPanel from "./NotificationGrantedPanel";

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

const StyledPushNotificationControls = styled.div`
  padding: 1rem;
  display: flex;
  align-items: center;
  border-radius: ${(props) => props.theme.borderRadius};
  background-color: ${(props) => props.theme.text50};
  width: calc(100% - 3rem);
  margin: 0 auto 1.5rem;
  gap: 1rem;

  p {
    flex: 1 1 auto;
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

  & > p {
    padding: 0 1.5rem 0.5rem;
    display: inline-block;
  }
`;

const InlineBlock = styled.span`
  display: inline-block;
`;

const PushNotificationControls = () => {
  const { isMobileApp } = useMobileApp();

  if (!isMobileApp) {
    return (
      <StyledPushNotificationControls>
        <p>Installez l'application pour recevoir des notifications</p>
      </StyledPushNotificationControls>
    );
  }

  return null;
};

const NotificationSettingPanel = (props) => {
  const {
    isOpen,
    close,
    notifications,
    activeNotifications,
    onChange,
    disabled,
    ready,
  } = props;

  const user = useSelector(getUser);

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
        {},
      ),
    [notifications],
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
        Paramètres de notifications&nbsp;<InlineBlock>et e-mails</InlineBlock>
      </h3>
      <p>
        Paramétrez la réception de vos e-mails et des notifications sur votre
        téléphone.
        <br />
        Vous recevez les e-mails sur votre adresse <u>{user.email}</u>&nbsp;
        <Link route="personalInformation">(modifier)</Link>
      </p>
      <div style={{ marginLeft: "20px", marginBottom: "20px" }}>
        <Button small link route="contactConfiguration">
          Gérer mes paramètres de contact
        </Button>
      </div>
      <div style={{ paddingLeft: "10px", paddingRight: "10px" }}>
        <NotificationGrantedPanel />
      </div>
      <PageFadeIn ready={ready}>
        <PushNotificationControls />
        {Object.keys(byType).map((type) => (
          <Accordion key={type} name={type} icon={icons[type] || "settings"}>
            <AccordionContent>
              {Object.keys(byType[type]).map((subtype) => (
                <StyledGroup key={subtype}>
                  <StyledGroupName>
                    <span>{subtype}</span>
                    <small>Téléphone</small>
                    <small>E-mail</small>
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
    }).isRequired,
  ),
  activeNotifications: PropTypes.object,
  onChange: PropTypes.func,
  disabled: PropTypes.bool,
  ready: PropTypes.bool,
};
export default NotificationSettingPanel;
