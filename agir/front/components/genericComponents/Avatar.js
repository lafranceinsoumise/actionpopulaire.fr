import PropTypes from "prop-types";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import { addQueryStringParams } from "@agir/lib/utils/url";

const UI_AVATARS_BASE_URL = "https://eu.ui-avatars.com/api/";
// API DOC @ https://eu.ui-avatars.com/
const UI_AVATARS_BASE_CONFIG = {
  size: 512,
  rounded: true,
  background: style.primary100,
  color: style.primary500,
  format: "svg",
};
const getAvatarImageURL = (name, image) => {
  if (image) {
    return image;
  }
  if (name) {
    return addQueryStringParams(UI_AVATARS_BASE_URL, {
      ...UI_AVATARS_BASE_CONFIG,
      name,
    });
  }
  return null;
};
const Avatar = styled.span.attrs(({ name, avatar }) => ({
  image: getAvatarImageURL(name, avatar),
  title: name,
}))`
  border-radius: 100%;
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center center;
  width: 4rem;
  height: 4rem;
  background-position: center center;
  background-image: ${({ image }) => `url(${image})`};
  display: ${({ image }) => (image ? "inline-block" : "none")};
`;
Avatar.propTypes = {
  name: PropTypes.string,
  avatar: PropTypes.string,
};
export default Avatar;
