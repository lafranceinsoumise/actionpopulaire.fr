import PropTypes from "prop-types";
import React, { useEffect, useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

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

  return decodeURIComponent(route);
};

const NotificationSettingLink = (props) => {
  const { root, iconLink = false } = props;
  const route = useNotificationSettingLink(root);
  const { isMobileApp } = useMobileApp();
  const dispatch = useDispatch();

  useEffect(() => {
    if (!isMobileApp) {
      dispatch(setTopBarRightLink(null));
    } else {
      dispatch(
        setTopBarRightLink({
          label: routeConfig.notificationSettings.label,
          to: route,
          protected: true,
        })
      );
    }
  }, [isMobileApp, dispatch, route]);

  if (iconLink) {
    return (
      <Link to={route} style={{ lineHeight: 0 }}>
        <RawFeatherIcon
          name="settings"
          color={style.black1000}
          width="1.5rem"
          height="1.5rem"
        />
      </Link>
    );
  }
  return (
    <StyledLink as="Link" to={route} icon="settings" small>
      Notifications et e-mails
    </StyledLink>
  );
};
NotificationSettingLink.propTypes = {
  root: PropTypes.string.isRequired,
  iconLink: PropTypes.bool,
};

export default NotificationSettingLink;
