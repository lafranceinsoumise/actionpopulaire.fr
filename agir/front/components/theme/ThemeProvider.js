import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import { createGlobalState } from "react-use";
import {
  StyleSheetManager,
  ThemeProvider as SCThemeProvider,
  createGlobalStyle,
} from "styled-components";

import { useLocalStorage } from "@agir/lib/utils/hooks";

import * as LIGHT_STYLE from "@agir/front/genericComponents/_variables-light.scss";
import * as DARK_STYLE from "@agir/front/genericComponents/_variables-dark.scss";

const STYLESHEETMANAGER_DEFAULT_PROPS = {
  enableVendorPrefixes: process.env.ENABLE_VENDOR_PREFIXES,
};

const GlobalStyle = createGlobalStyle`
  body {
    background-color: ${(props) => props.theme.background0};
    color: ${(props) => props.theme.textColor};
  }

  a {
    color: ${(props) => props.theme.linkColor};
  }

  a:hover,
  a:focus {
    color: ${(props) => props.theme.linkHoverColor};
  }


  h1,
  h2,
  h3,
  h4,
  h5,
  h6 {
    color: ${(props) => props.theme.textColor};
  }

  hr {
    border-top-color: ${(props) => props.theme.text50};
  }

  mark {
    color: ${(props) => props.theme.textColor};
    background-color: ${(props) => props.theme.markColor};
  }

  input,
  select,
  textarea {
    color: ${(props) => props.theme.textColor};
    background-color: ${(props) => props.theme.background0};
  }

  button {
    color: ${(props) => props.theme.textColor};
    background-color: ${(props) => props.theme.background100};
  }
`;

export const getTheme = (colorScheme) =>
  colorScheme === "dark" ? DARK_STYLE : LIGHT_STYLE;

const useGlobalSystemColorScheme = createGlobalState();
const useSystemColorScheme = () => {
  const [systemColorScheme, setSystemColorScheme] =
    useGlobalSystemColorScheme();

  const updateSystemColorScheme = useCallback(() => {
    const mode =
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
        ? "dark"
        : "light";

    if (mode !== systemColorScheme) {
      setSystemColorScheme(mode);
    }
  }, []);

  useEffect(() => {
    window
      .matchMedia("(prefers-color-scheme: dark)")
      .addEventListener("change", updateSystemColorScheme);

    updateSystemColorScheme();

    return () =>
      window
        .matchMedia("(prefers-color-scheme: dark)")
        .removeEventListener("change", updateSystemColorScheme);
  }, [updateSystemColorScheme]);

  return systemColorScheme;
};

const useGlobalColorScheme = createGlobalState();
export const useColorScheme = () => {
  const systemColorScheme = useSystemColorScheme();
  const [colorSchemeChoice, setColorSchemeChoice] = useLocalStorage(
    "AP__colorScheme",
    "auto",
  );
  const [globalColorScheme, setGlobalColorScheme] =
    useGlobalColorScheme(colorSchemeChoice);

  useEffect(() => {
    if (colorSchemeChoice !== "light" && colorSchemeChoice !== "dark") {
      setColorSchemeChoice("auto");
    }
    setGlobalColorScheme(
      colorSchemeChoice === "auto" ? systemColorScheme : colorSchemeChoice,
    );
  }, [colorSchemeChoice, setColorSchemeChoice, systemColorScheme]);

  return [globalColorScheme, setColorSchemeChoice, colorSchemeChoice];
};

const ThemeProvider = (props) => {
  const { children, styleSheetManagerProps = {}, theme, ...rest } = props;

  const [colorScheme] = useColorScheme();

  const currentTheme = useMemo(() => {
    const defaultTheme = getTheme(colorScheme);
    if (!theme) {
      return defaultTheme;
    }
    const customTheme = theme[colorScheme] || theme;
    return { ...customTheme, default: defaultTheme };
  }, [colorScheme, theme]);

  useEffect(() => {
    if (!colorScheme) {
      return;
    }
    document.documentElement.classList.forEach(
      (c) =>
        c.startsWith("AP_mode__") &&
        document.documentElement.classList.remove(c),
    );
    document.documentElement.classList.add(`AP_mode__${colorScheme}`);
  }, [colorScheme]);

  return (
    <StyleSheetManager
      {...STYLESHEETMANAGER_DEFAULT_PROPS}
      {...styleSheetManagerProps}
    >
      <SCThemeProvider theme={currentTheme} {...rest}>
        <GlobalStyle />
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
