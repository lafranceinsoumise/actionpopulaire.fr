import React from "react";
import { MobileAppModal } from "./MobileAppModal";

export default {
  component: MobileAppModal,
  title: "Layout/PushModal/MobileAppModal",
};

const Template = (args) => <MobileAppModal {...args} />;

export const Default = Template.bind({});
Default.args = {
  referralURL: "https://referral.url",
  shouldShow: true,
};
