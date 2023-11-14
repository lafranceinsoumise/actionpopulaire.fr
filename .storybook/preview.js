import { rest } from "msw";
import { initialize, mswDecorator } from "msw-storybook-addon";
import React, { useCallback, useEffect, useRef } from "react";
import { MemoryRouter } from "react-router-dom";
import { SWRConfig, useSWRConfig } from "swr";
import { ThemeProvider } from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import routes from "@agir/front/globalContext/nonReactRoutes.config";
import user from "@agir/front/mockData/user";

import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";

import "@agir/front/genericComponents/style.scss";
import "./style.css";

initialize({
  serviceWorker: {
    url: "/apiMockServiceWorker.js",
  },
});

export const parameters = {
  actions: { argTypesRegex: "^on[A-Z].*" },
  controls: { expanded: true },
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
      { name: "white", value: "white" },
      { name: "black25", value: style.black25 },
      { name: "black50", value: style.black50 },
      { name: "black100", value: style.black100 },
      { name: "black200", value: style.black200 },
      { name: "black500", value: style.black500 },
      { name: "black700", value: style.black700 },
      { name: "black1000", value: style.black1000 },
      {
        name: "primary-to-white",
        value: `no-repeat linear-gradient(0, white, ${style.primary500}) fixed`,
      },
      {
        name: "white-to-primary",
        value: `no-repeat linear-gradient(0, ${style.primary500}, white) fixed`,
      },
      {
        name: "striped",
        value: `no-repeat linear-gradient(-90deg, white 33%, ${style.secondary500} 33%, ${style.secondary500} 66%, ${style.primary500} 66%, ${style.primary500}) fixed`,
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
  (Story, context) => (
    <TestGlobalContextProvider
      value={{
        isSessionLoaded: true,
        routes,
        user: context.globals.auth === "authenticated" && user,
      }}
    >
      <MockSWRContext user={context.globals.auth === "authenticated" && user}>
        <ThemeProvider theme={style}>
          <MemoryRouter initialEntries={["/"]}>{Story()}</MemoryRouter>
        </ThemeProvider>
      </MockSWRContext>
    </TestGlobalContextProvider>
  ),
];
