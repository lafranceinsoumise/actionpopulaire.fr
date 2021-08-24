import React from "react";

import NewGroupPageModal from "./NewGroupPageModal";

export default {
  component: NewGroupPageModal,
  title: "Group/NewGroupPageModal",
};

const Template = (args) => {
  return <NewGroupPageModal {...args} />;
};

export const Default = Template.bind({});
Default.args = {
  isActive: true,
};
