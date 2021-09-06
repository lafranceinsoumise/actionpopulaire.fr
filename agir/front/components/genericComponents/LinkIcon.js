import PropTypes from "prop-types";
import React from "react";

import { FaFacebook, FaTwitter, FaYoutube, FaInstagram } from "react-icons/fa";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const LinkIcon = ({ url }) => {
  switch (true) {
    case /youtube.com/.test(url):
      return (
        <FaYoutube
          style={{ color: "#ff0000", width: "1rem", height: "1rem" }}
        />
      );
    case /twitter.com/.test(url):
      return (
        <FaTwitter
          style={{ color: "#1da1f2", width: "1rem", height: "1rem" }}
        />
      );
    case /facebook.com/.test(url):
      return (
        <FaFacebook
          style={{ color: "#1778f2", width: "1rem", height: "1rem" }}
        />
      );
    case /instagram.com/.test(url):
      return (
        <FaInstagram
          style={{ color: "#000000", width: "1rem", height: "1rem" }}
        />
      );
    default:
      return <RawFeatherIcon name="globe" width="1rem" height="1rem" />;
  }
};
LinkIcon.propTypes = {
  url: PropTypes.string,
};

export default LinkIcon;
