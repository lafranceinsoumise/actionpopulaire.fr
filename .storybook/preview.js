import React from "react";
import { MemoryRouter } from "react-router-dom";
import { ThemeProvider } from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import "./style.css";
import "../agir/front/components/genericComponents/style.scss";

export const parameters = {
  actions: { argTypesRegex: "^on[A-Z].*" },
  layout: "fullscreen",
};

export const decorators = [
  (Story) => (
    <ThemeProvider theme={style}>
      <MemoryRouter initialEntries={["/"]}>{Story()}</MemoryRouter>
    </ThemeProvider>
  ),
];
