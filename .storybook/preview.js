import React from "react";
import { MemoryRouter } from "react-router";

import "./style.css";
import "../agir/front/components/genericComponents/style.scss";

export const parameters = {
  actions: { argTypesRegex: "^on[A-Z].*" },
  layout: "fullscreen",
};

export const decorators = [
  (Story) => (
    <MemoryRouter initialEntries={["/"]}>
      <Story />
    </MemoryRouter>
  ),
];
