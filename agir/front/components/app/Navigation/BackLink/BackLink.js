import PropTypes from "prop-types";
import React, { useEffect, useMemo } from "react";
import styled from "styled-components";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Link from "@agir/front/app/Link";

import {
  useDispatch,
  useSelector,
} from "@agir/front/globalContext/GlobalContext";
import { getBackLink } from "@agir/front/globalContext/reducers";
import { routeConfig } from "@agir/front/app/routes.config";

import style from "@agir/front/genericComponents/_variables.scss";
import { useLocation } from "react-router-dom";
import { setBackLink } from "@agir/front/globalContext/actions";

const IconLink = styled(Link)`
  display: none;
  height: 2rem;
  width: 2rem;
  align-items: center;
  color: ${(props) => props.theme.black1000};
  line-height: 0;

  @media (max-width: ${style.collapse}px) {
    display: flex;
  }
`;

const IconTextLink = styled(Link)`
  font-weight: 600;
  font-size: 0.75rem;
  line-height: 1.4;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  margin: 2.5rem 1rem 1.5rem;

  &,
  &:hover,
  &:focus,
  &:active {
    text-decoration: none;
    color: #585858;
  }

  @media (max-width: ${style.collapse}px) {
    display: none;
  }
`;

const DEFAULT_ROUTE = {
  route: "events",
  label: "Retour à l'accueil",
};

export const useBackLink = (link) => {
  const backLink = useSelector(getBackLink);
  const dispatch = useDispatch();

  useEffect(() => {
    dispatch(setBackLink(link));
  }, [dispatch, link]);

  return backLink;
};

const BackLink = (props) => {
  const { children, icon = false, label, ...rest } = props;

  const { pathname, state } = useLocation();
  const backLink = useSelector(getBackLink);

  const linkProps = useMemo(() => {
    const linkProps = state?.backLink || backLink || DEFAULT_ROUTE;

    return {
      to: linkProps.to,
      route: linkProps.route,
      href: linkProps.href,
      params: linkProps.params,
      routeParams: linkProps.routeParams,
      state: linkProps.state,
      label: linkProps.label,
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [pathname, state]);

  const internalRouteConfig = useMemo(() => {
    return (linkProps?.route && routeConfig[linkProps.route]) || DEFAULT_ROUTE;
  }, [linkProps]);

  const linkLabel = useMemo(() => {
    if (label) {
      return label;
    }
    if (linkProps.label) {
      return linkProps.label;
    }
    if (internalRouteConfig?.label) {
      return internalRouteConfig.label;
    }
    return DEFAULT_ROUTE.label;
  }, [linkProps, internalRouteConfig, label]);

  return icon ? (
    <IconLink {...rest} {...linkProps} title={linkLabel} aria-label={linkLabel}>
      {children || (
        <RawFeatherIcon name="arrow-left" width="1.5rem" height="1.5rem" />
      )}
    </IconLink>
  ) : (
    <IconTextLink
      {...rest}
      {...linkProps}
      title={linkLabel}
      aria-label={linkLabel}
    >
      {children || (
        <>
          <RawFeatherIcon name="arrow-left" width="1rem" height="1rem" />
          &ensp;
          {linkLabel}
        </>
      )}
    </IconTextLink>
  );
};

BackLink.propTypes = {
  children: PropTypes.node,
  icon: PropTypes.bool,
  label: PropTypes.node,
};

export default BackLink;
