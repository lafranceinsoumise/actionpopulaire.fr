import React from "react";

import GroupPageCard from "./GroupPageCard";

export default {
  component: GroupPageCard,
  title: "Group/GroupPageCard",
};

const Template = (args) => {
  return <GroupPageCard {...args} />;
};

export const Default = Template.bind({});
Default.args = {
  children: "This is a group page card!",
  title: "Card title",
  editHref: "#edit",
  highlight: "crimson",
};
