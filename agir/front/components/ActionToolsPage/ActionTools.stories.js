import React from "react";

import { ActionTools } from "./ActionTools";

export default {
  component: ActionTools,
  title: "ActionToolsPage/ActionTools",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <ActionTools {...args} />;

export const Default = Template.bind({});
Default.args = {};
