import React from "react";

import { SubscriptionTypeModal } from "./SubscriptionTypeModal";

export default {
  component: SubscriptionTypeModal,
  title: "authentication/SubscriptionTypeModal",
  argTypes: {
    onConfirm: { table: { disable: true } },
    onCancel: { table: { disable: true } },
  },
};

const Template = (args) => <SubscriptionTypeModal {...args} />;

export const Default = Template.bind({});
Default.args = {
  type: "NSP",
  target: "event",
  shouldShow: true,
  isLoading: false,
};
