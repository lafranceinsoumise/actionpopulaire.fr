import React from "react";

import NoGroupCard from "./NoGroupCard";

export default {
  component: NoGroupCard,
  title: "CreateContactPage/NoGroupCard",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <NoGroupCard {...args} />;

export const Default = Template.bind({});
Default.args = {};
