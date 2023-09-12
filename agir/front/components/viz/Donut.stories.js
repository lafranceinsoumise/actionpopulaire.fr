import React from "react";

import Donut from "./Donut";

export default {
  component: Donut,
  title: "viz/Donut",
};

const Template = (args) => <Donut {...args} />;

export const Default = Template.bind({});
Default.args = {
  data: [
    {label: "Réponse A", value: 10},
    {label: "Réponse B", value: 15},
    {label: "Réponse C", value: 30}
  ],
  size: 200,
};
