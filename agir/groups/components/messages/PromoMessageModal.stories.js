import React from "react";

import { PromoMessageModal } from "./PromoMessageModal";

export default {
  component: PromoMessageModal,
  title: "Generic/PromoMessageModal",
};

const Template = (args) => {
  return (
    <PromoMessageModal {...args} />
  );
};

export const Default = Template.bind({});
Default.args = {
  shouldShow: true,
};
