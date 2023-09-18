import React from "react";

import InlineMenu from "./InlineMenu";
import Button from "./Button";

export default {
  component: InlineMenu,
  title: "Generic/InlineMenu",
  parameters: {
    layout: "padded",
  },
};

export const Default = (props) => (
  <p
    style={{
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      margin: "2rem",
    }}
  >
    <span style={{ fontSize: "3rem" }}>⟶&nbsp;</span>
    <InlineMenu {...props}>
      <ul>
        <li>
          <button>An action</button>
        </li>
        <li>
          <button>Another action</button>
        </li>
      </ul>
    </InlineMenu>
    <span style={{ fontSize: "3rem" }}>&nbsp;⟵</span>
  </p>
);

export const CustomTrigger = (props) => (
  <p
    style={{
      display: "flex",
      justifyContent: "center",
      alignItems: "center",
      margin: "2rem",
    }}
  >
    <span style={{ fontSize: "3rem" }}>⟶&nbsp;</span>
    <InlineMenu {...props} Trigger={Button}>
      <ul>
        <li>
          <button>An action</button>
        </li>
        <li>
          <button>Another action</button>
        </li>
      </ul>
    </InlineMenu>
    <span style={{ fontSize: "3rem" }}>&nbsp;⟵</span>
  </p>
);
