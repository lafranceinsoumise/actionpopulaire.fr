import React from "react";

import NotificationSettingGroup from "./NotificationSettingGroup";

export default {
  component: NotificationSettingGroup,
  title: "NotificationSettings/NotificationSettingGroup",
};

const Template = (args) => {
  return (
    <div style={{ padding: "1.5rem" }}>
      <NotificationSettingGroup {...args} />
      <NotificationSettingGroup {...args} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  name: "Compte et sécurité",
  notifications: [
    {
      id: "1",
      label: "Alertes de paiement et de sécurité",
      email: false,
      pushNotification: false,
    },
    {
      id: "2",
      label: "Rappels de don",
      email: true,
      pushNotification: false,
    },
    {
      id: "3",
      label: "Me rappeler mes tâches à faire régulièrement",
      pushNotification: false,
    },
  ],
  disabled: false,
};
