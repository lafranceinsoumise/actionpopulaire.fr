import React from "react";
import PropTypes from "prop-types";

import Card from "@agir/front/genericComponents/Card";
import facebookLogo from "@agir/front/genericComponents/logos/facebook.svg";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

const EventFacebookLinkCard = ({ routes: { facebook } }) => (
  <Card>
    <img
      src={facebookLogo}
      alt="Facebook"
      height="24"
      width="24"
      style={{ marginRight: "16px" }}
    />
    <a href={facebook} style={{ fontWeight: 500 }}>
      L'événement sur Facebook
      <span style={{ marginLeft: "8px" }}>
        <FeatherIcon name="external-link" inline small />
      </span>
    </a>
  </Card>
);

EventFacebookLinkCard.propTypes = {
  routes: PropTypes.shape({ facebook: PropTypes.string }),
};

export default EventFacebookLinkCard;
