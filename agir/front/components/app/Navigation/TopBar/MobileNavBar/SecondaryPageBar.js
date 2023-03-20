import PropTypes from "prop-types";
import React from "react";

import RightLink from "./RightLink";
import StyledBar from "./StyledBar";
import BackLink from "@agir/front/app/Navigation/BackLink";

const SecondaryPageBar = (props) => {
  const { isLoading, title, user, settingsLink } = props;

  return (
    <StyledBar>
      <BackLink icon />
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
  settingsLink: PropTypes.object,
  user: PropTypes.oneOfType([PropTypes.object, PropTypes.bool]),
};

export default SecondaryPageBar;
