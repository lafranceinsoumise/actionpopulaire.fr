import React from "react";
import Card from "../../../front/components/genericComponents/Card";
import facebookLogo from "../../../front/components/genericComponents/logos/facebook.svg";
import PropTypes from "prop-types";
import FeatherIcon from "../../../front/components/genericComponents/FeatherIcon";

const FacebookLink = ({ facebookUrl }) => (
  <Card>
    <img
      src={facebookLogo}
      alt="Facebook"
      height="24"
      style={{ marginRight: "16px" }}
    />
    <a href={facebookUrl} style={{ fontWeight: 500 }}>
      L'événement sur Facebook
      <span style={{ marginLeft: "8px" }}>
        <FeatherIcon name="external-link" inline small />
      </span>
    </a>
  </Card>
);

FacebookLink.propTypes = {
  facebookUrl: PropTypes.string,
};

export default FacebookLink;
