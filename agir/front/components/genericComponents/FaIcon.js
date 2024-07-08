/* eslint-disable react/prop-types */
/* eslint-disable react/display-name */
import React from "react";
import styled, { useTheme } from "styled-components";

import fontawesome from "@agir/lib/utils/fontawesome";

const iconProps = ["icon", "color", "size"];

const StyledIcon = styled.i.withConfig({
  shouldForwardProp: (prop) => !iconProps.includes(prop),
})`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  margin: 0;
  padding: 0;
  line-height: inherit;
  text-decoration: none;
  color: ${(props) => props.color || "currentColor"};
  font-size: ${(props) => {
    if (!props.size) {
      return "1em";
    }
    if (typeof props.size !== "number") {
      return props.size;
    }
    return props.size + "px";
  }};
`;

const FaIcon =
  (defaultIcon) =>
  ({ icon, className, color, ...props }) => {
    const iconConfig = fontawesome(icon || defaultIcon, true);
    const theme = useTheme();

    return (
      <StyledIcon
        {...props}
        color={theme[color] || color}
        className={`${className} ${iconConfig?.className}`.trim()}
      />
    );
  };

export const FaBullhorn = FaIcon("bullhorn");
export const FaCalendar = FaIcon("calendar");
export const FaComment = FaIcon("comment");
export const FaComments = FaIcon("comments");
export const FaExclamation = FaIcon("exclamation");
export const FaFacebook = FaIcon("facebook-official");
export const FaInstagram = FaIcon("instagram");
export const FaLock = FaIcon("lock");
export const FaTelegram = FaIcon("telegram");
export const FaTwitter = FaIcon("twitter");
export const FaUsers = FaIcon("users");
export const FaWhatsapp = FaIcon("whatsapp");
export const FaYoutube = FaIcon("youtube-play");
export const FaMicrophone = FaIcon("microphone");

export default FaIcon();
