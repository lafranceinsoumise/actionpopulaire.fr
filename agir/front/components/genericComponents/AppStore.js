import React, { useMemo } from "react";
import PropTypes from "prop-types";
import styled from "styled-components";

import { addQueryStringParams } from "@agir/lib/utils/url";

import APP_STORE_APPLE from "@agir/front/genericComponents/logos/appstore_apple.svg";
import APP_STORE_GOOGLE from "@agir/front/genericComponents/logos/appstore_google.svg";

const CONFIG = {
  apple: {
    href: "https://infos.actionpopulaire.fr/application-ios",
    title: "Télécharger dans l'App Store",
    $image: APP_STORE_APPLE,
  },
  google: {
    href: "https://infos.actionpopulaire.fr/application-android",
    title: "Disponible sur Google Play",
    $image: APP_STORE_GOOGLE,
  },
};

const DEFAULT_UTM_PARAMS = {
  utm_source: "ap",
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
  const { type, params, ...rest } = props;
  const config = CONFIG[type];

  const href = useMemo(() => {
    if (config && config.href) {
      return addQueryStringParams(config.href, params || DEFAULT_UTM_PARAMS);
    }
  }, [config, params]);

  if (!config) {
    return null;
  }

  return <AppStoreLink {...config} {...rest} href={href} />;
};

AppStore.propTypes = {
  type: PropTypes.oneOf(Object.keys(CONFIG)).isRequired,
  params: PropTypes.object,
};

export default AppStore;
