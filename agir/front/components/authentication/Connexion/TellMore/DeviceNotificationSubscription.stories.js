import React from "react";

import DeviceNotificationSubscription from "./DeviceNotificationSubscription";

export default {
  component: DeviceNotificationSubscription,
  title: "Authentication/DeviceNotificationSubscription",
};

const Template = (args) => {
  return <DeviceNotificationSubscription {...args} />;
};

export const Default = Template.bind({});
Default.args = {};
