import React from "react";

import user from "@agir/front/mockData/user";
import SoftLoginModal, { SOFT_LOGIN_MODAL_TAGS } from "./SoftLoginModal";

export default {
  component: SoftLoginModal,
  title: "authentication/SoftLoginModal",
};

const Template = (args) => <SoftLoginModal {...args} />;

export const Anonymous = Template.bind({});
Anonymous.args = {
  shouldShow: true,
  user,
  data: {
    tags: SOFT_LOGIN_MODAL_TAGS[0],
  },
};

export const Authenticated = Template.bind({});
Authenticated.args = {
  shouldShow: true,
  user,
  data: {
    tags: [SOFT_LOGIN_MODAL_TAGS[1], "Foo", "foo@bar.com", "#"].join(","),
  },
};
