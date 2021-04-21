import React from "react";

import DeviceNotificationSubscription from "./DeviceNotificationSubscription";
import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";

export default {
  component: DeviceNotificationSubscription,
  title: "Authentication/DeviceNotificationSubscription",
};

const Template = (args) => {
  return (
    <TestGlobalContextProvider>
      <DeviceNotificationSubscription {...args} />
    </TestGlobalContextProvider>
  );
};

export const Default = Template.bind({});
Default.args = {};
