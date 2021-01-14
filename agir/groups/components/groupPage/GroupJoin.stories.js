import React from "react";

import GroupJoin from "./GroupJoin";

export default {
  component: GroupJoin,
  title: "Group/GroupJoin",
};

const Template = (args) => {
  return <GroupJoin {...args} />;
};

export const Default = Template.bind({});
Default.args = {
  url: "#join",
  is2022: false,
};
