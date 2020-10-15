import React from "react";
import PropTypes from "prop-types";
import { ThemeProvider } from "styled-components";

import styles from "./style.scss";

const routes = new Proxy(
  {},
  {
    get(_target, name) {
      return `#${name}`;
    },
  }
);

const Config = React.createContext({
  user: null,
  domain: "https://agir.lafranceinsoumise.fr",
  routes,
});

export const ConfigProvider = ({ children }) => {
  const configScript = document.getElementById("configContext");
  let config = null;

  if (configScript) {
    config = JSON.parse(configScript.textContent);
  }

  return (
    <Config.Provider value={config}>
      <ThemeProvider theme={styles}>{children}</ThemeProvider>
    </Config.Provider>
  );
};
ConfigProvider.propTypes = {
  children: PropTypes.element,
};

export const useConfig = () => React.useContext(Config);

export const TestConfigProvider = Config.Provider;
