import PropTypes from "prop-types";
import React from "react";

import {
  FaFacebook,
  FaTwitter,
  FaYoutube,
  FaInstagram,
  FaTelegram,
} from "@agir/front/genericComponents/FaIcon";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { useTheme } from "styled-components";

const LinkIcon = ({ url }) => {
  const theme = useTheme();

  switch (true) {
    case /actionpopulaire.fr/i.test(url):
      return (
        <svg width="16" height="16" viewBox="0 0 140 154" fill="none">
          <path
            d="M84.4375 153.082L45.725 114.503C24.3446 93.1968 24.1768 58.8196 45.3502 37.7196C66.5236 16.6195 101.02 16.7867 122.401 38.093C143.781 59.3993 143.949 93.7765 122.775 114.877L84.4375 153.082Z"
            fill={theme.secondary500}
          />
          <path
            fillRule="evenodd"
            clipRule="evenodd"
            d="M26.4559 86.8027L57.0078 117.249L87.5597 86.8027C104.433 69.9878 104.433 42.7254 87.5597 25.9104C70.6864 9.0955 43.3292 9.0955 26.4559 25.9104C9.58251 42.7254 9.58251 69.9878 26.4559 86.8027ZM57.0078 135.652L96.7933 96.0043C118.766 74.1075 118.766 38.6057 96.7933 16.7089C74.8204 -5.18792 39.1952 -5.18792 17.2224 16.7089C-4.75054 38.6057 -4.75054 74.1075 17.2224 96.0043L57.0078 135.652Z"
            fill={theme.text1000}
          />
        </svg>
      );
    case /youtube\.com|youtu\.be/i.test(url):
      return (
        <span
          style={{
            background: `radial-gradient(circle, ${theme.white} 0%, ${theme.white} 40%, transparent 40%, transparent)`,
            lineHeight: 0,
            borderRadius: "100%",
            textAlign: "center",
          }}
        >
          <FaYoutube
            style={{ color: "#ff0000", width: "1rem", height: "1rem" }}
          />
        </span>
      );
    case /^x\.com/i.test(url):
    case /\/x\.com/i.test(url):
    case /twitter\.com/i.test(url):
      return (
        <FaTwitter
          style={{ color: "#1da1f2", width: "1rem", height: "1rem" }}
        />
      );
    case /(?:https?:\/\/)?(?:www\.)?(mbasic.facebook|m\.facebook|facebook|fb)\.(com|me)\/(?:(?:\w\.)*#!\/)?(?:pages\/)?(?:[\w\-\.]*\/)*([\w\-\.]*)/i.test(
      url,
    ):
      return (
        <span
          style={{
            background: `radial-gradient(circle, ${theme.white} 0%, ${theme.white} 50%, ${theme.facebook} 50%, ${theme.facebook} 100%)`,
            lineHeight: 0,
            borderRadius: "100%",
            textAlign: "center",
          }}
        >
          <FaFacebook
            style={{ color: theme.facebook, width: "1rem", height: "1rem" }}
          />
        </span>
      );
    case /(?:(?:http|https):\/\/)?(?:www.)?(?:instagram\.com|instagr.am|instagr\.com)\/(\w+)/i.test(
      url,
    ):
      return (
        <FaInstagram
          style={{ color: theme.text1000, width: "1rem", height: "1rem" }}
        />
      );
    case /^t.me/i.test(url):
    case /\/t.me/i.test(url):
    case /telegram.me/i.test(url):
      return (
        <span
          style={{
            background: `radial-gradient(circle, ${theme.white} 0%, ${theme.white} 50%, ${theme.telegram} 50%, ${theme.telegram} 100%)`,
            lineHeight: 0,
            borderRadius: "100%",
          }}
        >
          <FaTelegram
            style={{ color: theme.telegram, width: "1rem", height: "1rem" }}
          />
        </span>
      );
    default:
      return <RawFeatherIcon name="globe" width="1rem" height="1rem" />;
  }
};
LinkIcon.propTypes = {
  url: PropTypes.string,
};

export default LinkIcon;
