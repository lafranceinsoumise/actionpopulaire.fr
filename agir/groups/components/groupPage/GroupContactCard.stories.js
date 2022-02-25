import React from "react";

import GroupContactCard from "./GroupContactCard";

export default {
  component: GroupContactCard,
  title: "Group/GroupContactCard",
};

const Template = (args) => {
  return <GroupContactCard {...args} />;
};

export const Default = Template.bind({});
Default.args = {
  contact: {
    name: "Isabelle Guérini",
    email: "isabelini@gmail.com",
    phone: "06 42 23 12 01",
    hidePhone: false,
  },
  editLinkTo: "/edit/",
};
