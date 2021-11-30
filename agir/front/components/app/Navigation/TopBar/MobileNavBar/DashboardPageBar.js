import PropTypes from "prop-types";
import React from "react";

import { routeConfig } from "@agir/front/app/routes.config";

import Link from "@agir/front/app/Link";
import LogoAP from "@agir/front/genericComponents/LogoAP";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import RightLink from "./RightLink";
import StyledBar, { IconLink } from "./StyledBar";

export const DashboardPageBar = (props) => {
  const { isLoading, user, settingsLink, hasSearchLink } = props;
  return (
    <StyledBar>
      {hasSearchLink ? (
        <IconLink route="search">
          <RawFeatherIcon name="search" />
        </IconLink>
      ) : (
        <IconLink href={routeConfig.events.getLink()}>
          <RawFeatherIcon name="arrow-left" width="24px" height="24px" />
        </IconLink>
      )}
      <h1>
        <Link href={routeConfig.events.getLink()}>
          <LogoAP small style={{ height: "36px", width: "auto" }} />
        </Link>
      </h1>
      <RightLink
        isLoading={isLoading}
        user={user}
        settingsLink={settingsLink}
      />
    </StyledBar>
  );
};
DashboardPageBar.propTypes = {
  isLoading: PropTypes.bool,
  settingsLink: PropTypes.object,
  user: PropTypes.oneOfType([PropTypes.object, PropTypes.bool]),
  hasSearchLink: PropTypes.bool,
};
export default DashboardPageBar;
