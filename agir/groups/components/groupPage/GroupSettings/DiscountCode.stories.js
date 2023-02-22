import React from "react";

import DiscountCode from "./DiscountCode.js";

export default {
  component: DiscountCode,
  title: "GroupSettings/DiscountCode",
};

const Template = (args) => <DiscountCode {...args} />;

export const Default = Template.bind({});

Default.args = {
  code: "ZEziAujKIhjBJhjHuhguyuY",
  expiration: "2022-01-01 00:00:00",
};
