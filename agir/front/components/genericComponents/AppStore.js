import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";

import APP_STORE_APPLE from "@agir/front/genericComponents/logos/appstore_apple.svg";

const CONFIG = {
  apple: {
    href:
      "https://apps.apple.com/us/app/action-populaire/id1559737444#?platform=iphone",
    title: "Télécharger dans l'App Store",
    $image: APP_STORE_APPLE,
  },
};

const AppStoreLink = styled.a`
  display: block;
  width: 170px;
  height: 50px;
  background: url(${({ $image }) => $image});
  background-size: cover;
  background-position: center center;
  border-radius: 0.5px;
  cursor: pointer;
`;

const AppStore = (props) => {
  const { type, ...rest } = props;
  const config = CONFIG[type];

  if (!config) {
    return;
  }

  return <AppStoreLink {...config} {...rest} />;
};

AppStore.propTypes = {
  type: PropTypes.oneOf(Object.keys(CONFIG)),
};

export default AppStore;
