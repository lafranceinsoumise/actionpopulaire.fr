import PropTypes from "prop-types";
import React from "react";

import { routeConfig } from "@agir/front/app/routes.config";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import RightLink from "./RightLink";
import StyledBar, { IconLink } from "./StyledBar";

const defaultBackLink = {
  href: routeConfig.events.getLink(),
  to: routeConfig.events.getLink(),
  label: routeConfig.events.label,
};

const SecondaryPageBar = (props) => {
  const { isLoading, title, user, settingsLink } = props;
  const backLink = props.backLink || defaultBackLink;

  return (
    <StyledBar>
      <IconLink
        to={backLink.to}
        href={backLink.href}
        route={backLink.route}
        title={backLink.label}
        aria-label={backLink.label}
      >
        <RawFeatherIcon name="arrow-left" width="24px" height="24px" />
      </IconLink>
      <h2>{title}</h2>
      <RightLink
        isLoading={isLoading}
        user={user}
        settingsLink={settingsLink}
      />
    </StyledBar>
  );
};

SecondaryPageBar.propTypes = {
  isLoading: PropTypes.bool,
  title: PropTypes.string,
  backLink: PropTypes.object,
  settingsLink: PropTypes.object,
  user: PropTypes.oneOfType([PropTypes.object, PropTypes.bool]),
};

export default SecondaryPageBar;
