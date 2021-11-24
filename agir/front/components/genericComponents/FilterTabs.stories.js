import React from "react";

import FilterTabs from "./FilterTabs";

export default {
  component: FilterTabs,
  title: "Generic/FilterTabs",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <FilterTabs {...args} />;

export const Default = Template.bind({});
Default.args = {
  tabs: [
    "Tout",
    "Autres",
    "Le reste",
    "Encore plus",
    "Toujours plus",
    "C'est sans fin",
  ],
  activeTab: 0,
};
