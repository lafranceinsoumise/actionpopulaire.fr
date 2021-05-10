import React from "react";

import GroupLink from "./GroupLink.js";

export default {
  component: GroupLink,
  title: "GroupSettings/GroupLink",
};

const Template = (args) => <GroupLink {...args} />;

export const Default = Template.bind({});

Default.args = {
  label: "Présentation Youtube",
  url: "https://actionpopulaire.fr",
};
