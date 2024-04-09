import PropTypes from "prop-types";
import React from "react";
import {
  StyleSheetManager,
  ThemeProvider as SCThemeProvider,
} from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

const STYLESHEETMANAGER_DEFAULT_PROPS = {
  enableVendorPrefixes: process.env.ENABLE_VENDOR_PREFIXES,
};

const ThemeProvider = (props) => {
  const { children, styleSheetManagerProps = {}, ...rest } = props;

  return (
    <StyleSheetManager
      {...STYLESHEETMANAGER_DEFAULT_PROPS}
      {...styleSheetManagerProps}
    >
      <SCThemeProvider theme={style} {...rest}>
        {children}
      </SCThemeProvider>
    </StyleSheetManager>
  );
};

ThemeProvider.propTypes = {
  children: PropTypes.node,
  styleSheetManagerProps: PropTypes.object,
};

export default ThemeProvider;
