import PropTypes from "prop-types";
import React, { useEffect, useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";

import { routeConfig } from "@agir/front/app/routes.config";
import { useMobileApp } from "@agir/front/app/hooks";

import { useDispatch } from "@agir/front/globalContext/GlobalContext";

import { setTopBarRightLink } from "@agir/front/globalContext/actions";

const StyledLink = styled(Button)`
  margin-left: auto;
  @media (max-width: ${style.collapse}px) {
    display: none;
  }
`;

export const useNotificationSettingLink = (root) => {
  const route = useMemo(
    () =>
      root
        ? routeConfig.notificationSettings.getLink({ root })
        : routeConfig.notificationSettings.getLink(),
    [root]
  );

  return route;
};

const NotificationSettingLink = (props) => {
  const { root } = props;
  const route = useNotificationSettingLink(root);
  const { isMobileApp } = useMobileApp();
  const dispatch = useDispatch();

  useEffect(() => {
    if (!isMobileApp) {
      dispatch(setTopBarRightLink(null));
    }
  }, [isMobileApp, dispatch]);

  return (
    <StyledLink as="Link" to={route} icon="settings" small>
      Notifications et e-mails
    </StyledLink>
  );
};
NotificationSettingLink.propTypes = {
  root: PropTypes.string.isRequired,
};

export default NotificationSettingLink;
