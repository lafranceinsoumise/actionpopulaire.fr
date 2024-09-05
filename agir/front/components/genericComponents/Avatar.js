import PropTypes from "prop-types";
import styled from "styled-components";

import { addQueryStringParams } from "@agir/lib/utils/url";

const UI_AVATARS_BASE_URL = "https://eu.ui-avatars.com/api/";
// API DOC @ https://eu.ui-avatars.com/
const UI_AVATARS_BASE_CONFIG = {
  size: 512,
  rounded: true,
  format: "svg",
};
const getAvatarImageURL = (name, image, config) => {
  if (image) {
    return image;
  }
  if (name) {
    return addQueryStringParams(UI_AVATARS_BASE_URL, {
      ...UI_AVATARS_BASE_CONFIG,
      ...config,
      name,
    });
  }
  return null;
};
const Avatar = styled.span
  .withConfig({
    shouldForwardProp: (prop) =>
      !["name", "displayName", "image"].includes(prop),
  })
  .attrs(({ name, displayName, image, theme }) => ({
    image: getAvatarImageURL(name || displayName, image, {
      background: theme.primary100,
      color: theme.primary500,
    }),
    title: name || displayName,
  }))`
  width: 4rem;
  height: 4rem;
  border-radius: 100%;
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center center;
  background-image: ${({ image }) => `url(${image})`};
  display: ${({ image }) => (image ? "inline-block" : "none")};
`;
Avatar.propTypes = {
  name: PropTypes.string,
  displayName: PropTypes.string,
  image: PropTypes.string,
};
export default Avatar;
