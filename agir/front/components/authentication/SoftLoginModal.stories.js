import React from "react";

import user from "@agir/front/mockData/user";
import SoftLoginModal from "./SoftLoginModal";

export default {
  component: SoftLoginModal,
  title: "authentication/SoftLoginModal",
};

const Template = (args) => <SoftLoginModal {...args} />;

export const Default = Template.bind({});
Default.args = {
  shouldShow: true,
  user,
};
