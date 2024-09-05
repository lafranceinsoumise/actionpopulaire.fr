import { DocsContainer } from "@storybook/blocks";
import { addons } from "@storybook/preview-api";
import { themes } from "@storybook/theming";
import { initialize, mswDecorator } from "msw-storybook-addon";
import React, { useCallback, useEffect, useRef, useState } from "react";
import { MemoryRouter } from "react-router-dom";
import { DARK_MODE_EVENT_NAME, useDarkMode } from "storybook-dark-mode";
import { SWRConfig } from "swr";

import * as DARK_THEME from "@agir/front/genericComponents/_variables-dark.scss";
import * as LIGHT_THEME from "@agir/front/genericComponents/_variables-light.scss";

import routes from "@agir/front/globalContext/nonReactRoutes.config";
import user from "@agir/front/mockData/user";

import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";
import ThemeProvider from "@agir/front/theme/ThemeProvider";
import { getTheme } from "../agir/front/components/theme/ThemeProvider";

import "@agir/front/genericComponents/style.scss";
import "./style.css";

initialize({
  serviceWorker: {
    url: "/apiMockServiceWorker.js",
  },
});

const channel = addons.getChannel();

const themeBase = {
  fontBase: LIGHT_THEME.fontFamilyBase,
  brandTitle: "Storybook Action populaire",
  brandUrl: "https://actionpopulaire.fr",
  brandImage: "https://media.actionpopulaire.fr/logo_light.png",
  brandTarget: "_self",
};

const lightTheme = {
  ...themes.light,
  ...themeBase,
  appBg: LIGHT_THEME.background25,
  appBorderColor: LIGHT_THEME.text50,
  appContentBg: LIGHT_THEME.background0,
  appPreviewBg: LIGHT_THEME.background0,
  barBg: LIGHT_THEME.background25,
  barHoverColor: LIGHT_THEME.primary500,
  barSelectedColor: LIGHT_THEME.primary500,
  barTextColor: LIGHT_THEME.text500,
  booleanBg: LIGHT_THEME.background25,
  booleanSelectedBg: LIGHT_THEME.primary500,
  buttonBg: LIGHT_THEME.background25,
  buttonBorder: LIGHT_THEME.text50,
  colorPrimary: LIGHT_THEME.primary500,
  colorSecondary: LIGHT_THEME.primary500,
  inputBg: LIGHT_THEME.background0,
  inputBorder: LIGHT_THEME.text50,
  inputTextColor: LIGHT_THEME.text1000,
  textColor: LIGHT_THEME.text1000,
  textInverseColor: LIGHT_THEME.background25,
  textMutedColor: LIGHT_THEME.text700,
};
const darkTheme = {
  ...themes.dark,
  ...themeBase,
  brandImage: "https://media.actionpopulaire.fr/logo_dark.png",
  appBg: DARK_THEME.background25,
  appBorderColor: DARK_THEME.text50,
  appContentBg: DARK_THEME.background0,
  appPreviewBg: DARK_THEME.background0,
  barBg: DARK_THEME.background25,
  barHoverColor: DARK_THEME.primary500,
  barSelectedColor: DARK_THEME.primary600,
  barTextColor: DARK_THEME.text500,
  booleanBg: DARK_THEME.background25,
  booleanSelectedBg: DARK_THEME.primary600,
  buttonBg: DARK_THEME.primary500,
  buttonBorder: DARK_THEME.text50,
  colorPrimary: DARK_THEME.primary500,
  colorSecondary: DARK_THEME.primary500,
  inputBg: DARK_THEME.background0,
  inputBorder: DARK_THEME.text50,
  inputTextColor: DARK_THEME.text1000,
  textColor: DARK_THEME.text1000,
  textInverseColor: DARK_THEME.background25,
  textMutedColor: DARK_THEME.text700,
};

const CustomDocsContainer = ({ children, ...props }) => {
  const [isDark, setIsDark] = useState();

  useEffect(() => {
    channel.on(DARK_MODE_EVENT_NAME, setIsDark);
    return () => channel.removeListener(DARK_MODE_EVENT_NAME, setIsDark);
  }, []);

  const theme = isDark ? darkTheme : lightTheme;

  return (
    <DocsContainer {...props} theme={theme}>
      {children}
    </DocsContainer>
  );
};

export const parameters = {
  actions: { argTypesRegex: "^on[A-Z].*" },
  controls: { expanded: true },
  darkMode: {
    current: "light",
    dark: darkTheme,
    light: lightTheme,
  },
  docs: { container: CustomDocsContainer },
  layout: "fullscreen",
  backgrounds: {
    default: "transparent",
    grid: {
      cellSize: 4,
      opacity: 0.5,
      cellAmount: 5,
    },
    values: [
      { name: "transparent", value: "transparent" },
      { name: "white", value: LIGHT_THEME.background0 },
      { name: "black25", value: LIGHT_THEME.background25 },
      { name: "black50", value: LIGHT_THEME.background50 },
      { name: "black100", value: LIGHT_THEME.background100 },
      { name: "black200", value: LIGHT_THEME.background200 },
      { name: "black500", value: LIGHT_THEME.backgroun500 },
      { name: "black700", value: LIGHT_THEME.background700 },
      { name: "black1000", value: LIGHT_THEME.text1000 },
      {
        name: "primary-to-white",
        value: `no-repeat linear-gradient(0, white, ${LIGHT_THEME.primary500}) fixed`,
      },
      {
        name: "white-to-primary",
        value: `no-repeat linear-gradient(0, ${LIGHT_THEME.primary500}, white) fixed`,
      },
      {
        name: "striped",
        value: `no-repeat linear-gradient(-90deg, white 33%, ${LIGHT_THEME.secondary500} 33%, ${LIGHT_THEME.secondary500} 66%, ${LIGHT_THEME.primary500} 66%, ${LIGHT_THEME.primary500}) fixed`,
      },
    ],
  },
};

export const globalTypes = {
  auth: {
    name: "Current user",
    description: "Currently authenticated user for components",
    defaultValue: "authenticated",
    toolbar: {
      icon: "user",
      // Array of plain string values or MenuItem shape (see below)
      items: [
        {
          icon: "eyeclose",
          value: "anonymous",
          title: "Anonymous user",
        },
        {
          icon: "eye",
          value: "authenticated",
          title: "Authenticated user",
        },
      ],
      // Property that specifies if the name of the item will be displayed
      showName: false,
    },
  },
};

const MockSWRContext = ({ user = false, children }) => {
  const sessionRef = useRef({ user });
  const mockFetcher = useCallback(async (args) => {
    if (!Array.isArray(args)) {
      args = [args];
    }

    const [url, method = "GET"] = args;

    if (url.endsWith("/api/session/")) {
      return Promise.resolve(sessionRef.current);
    }

    const res = await fetch(url, { method });

    return res.json();
  }, []);

  useEffect(() => {
    sessionRef.current = { user };
  }, [user]);

  return (
    <SWRConfig value={{ fetcher: mockFetcher, provider: () => new Map() }}>
      {children}
    </SWRConfig>
  );
};

export const decorators = [
  mswDecorator,
  (Story, context) => {
    const isDark = useDarkMode();
    const theme = getTheme(isDark ? "dark" : "light");

    useEffect(() => {
      channel.emit(DARK_MODE_EVENT_NAME, isDark);
    }, []);

    return (
      <TestGlobalContextProvider
        value={{
          isSessionLoaded: true,
          routes,
          user: context.globals.auth === "authenticated" && user,
        }}
      >
        <MockSWRContext user={context.globals.auth === "authenticated" && user}>
          <ThemeProvider theme={theme}>
            <MemoryRouter initialEntries={["/"]}>{Story()}</MemoryRouter>
          </ThemeProvider>
        </MockSWRContext>
      </TestGlobalContextProvider>
    );
  },
];
