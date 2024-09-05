import React from "react";

import SecondaryActions from "./SecondaryActions";

export default {
  component: SecondaryActions,
  title: "Group/GroupUserActions/SecondaryActions",
  parameters: {
    layout: "centered",
  },
};

const Template = (args) => (
  <div style={{ maxWidth: "100%", width: "320px" }}>
    <SecondaryActions {...args} />
  </div>
);

export const Default = Template.bind({});
Default.args = {
  id: "abc",
  isCertified: true,
  routes: {},
  contact: {
    email: "contact@groupe.com",
  },
};
