import React from "react";

import NotificationSettings from "./NotificationSettings";
import notifications from "@agir/front/mockData/notificationSettings";

export default {
  component: NotificationSettings,
  title: "NotificationSettings/NotificationSettings",
};

const Template = (args) => {
  const [isOpen, setIsOpen] = React.useState(true);
  const close = React.useCallback(() => setIsOpen(false), []);
  return <NotificationSettings {...args} isOpen={isOpen} close={close} />;
};

export const Default = Template.bind({});
Default.args = {
  notifications,
  disabled: false,
};
