import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";

import { routeConfig } from "@agir/front/app/routes.config";

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
  return (
    <StyledLink as="Link" to={route} icon="settings" small>
      Paramètres de notifications
    </StyledLink>
  );
};
NotificationSettingLink.propTypes = {
  root: PropTypes.string.isRequired,
};

export default NotificationSettingLink;
