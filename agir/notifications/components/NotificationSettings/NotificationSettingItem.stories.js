import React from "react";

import NotificationSettingItem from "./NotificationSettingItem";

export default {
  component: NotificationSettingItem,
  title: "NotificationSettings/NotificationSettingItem",
};

const Template = (args) => {
  const [value, setValue] = React.useState(args.notification);
  const handleChange = React.useCallback((notification) => {
    setValue(notification);
  }, []);

  return (
    <div style={{ padding: "1.5rem" }}>
      <NotificationSettingItem
        {...args}
        notification={value}
        onChange={handleChange}
      />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  notification: {
    id: "1",
    label: "Alertes de paiement et de sécurité",
    email: true,
    pushNotification: false,
  },
  email: true,
  push: false,
  disabled: false,
};

export const EmailOnly = Template.bind({});
EmailOnly.args = {
  ...Default.args,
  notification: {
    ...Default.args.notification,
    hasPush: false,
  },
};

export const PushOnly = Template.bind({});
PushOnly.args = {
  ...Default.args,
  notification: {
    ...Default.args.notification,
    hasEmail: false,
    email: undefined,
  },
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Default.args,
  disabled: true,
  email: true,
};
