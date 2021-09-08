import React from "react";

import NotificationSettingPanel from "./NotificationSettingPanel";
import notifications from "@agir/front/mockData/notificationSettings";

export default {
  component: NotificationSettingPanel,
  title: "NotificationSettings/NotificationSettingPanel",
};

const Template = (args) => {
  const [isOpen, setIsOpen] = React.useState(true);
  const close = React.useCallback(() => setIsOpen(false), []);
  return <NotificationSettingPanel {...args} isOpen={isOpen} close={close} />;
};

export const Default = Template.bind({});
Default.args = {
  notifications,
  disabled: false,
  ready: true,
  activeNotifications: [],
};

export const withDeviceSubscription = Template.bind({});
withDeviceSubscription.args = {
  ...Default.args,
  subscribeDevice: console.log,
};
