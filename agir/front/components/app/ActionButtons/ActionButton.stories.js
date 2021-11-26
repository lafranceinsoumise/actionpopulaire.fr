import React from "react";

import ACTIONS from "./actions.config";

import ActionButton from "./ActionButton";

export default {
  component: ActionButton,
  title: "app/ActionButtons/ActionButton",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) =>
  Object.entries(ACTIONS).map(([key, action]) => (
    <span key={key} style={{ padding: ".25rem" }}>
      <ActionButton {...action} />
    </span>
  ));

export const Default = Template.bind({});
Default.args = {};
