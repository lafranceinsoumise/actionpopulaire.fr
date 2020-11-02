import React from "react";

import RequiredActionCard from "./RequiredActionCard";

export default {
  component: RequiredActionCard,
  title: "Generic/RequiredActionCard",
  argTypes: {
    onConfirm: { action: "onConfirm" },
    onDismiss: { action: "onDismiss" },
  },
};

const Template = (args) => {
  return (
    <div
      style={{
        maxWidth: 396,
        margin: "10px auto",
      }}
    >
      <RequiredActionCard {...args} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  name: "waiting-location-event",
  text: "Précisez la localisation de votre événement : {événement}",
  iconName: "alert-circle",
  confirmLabel: "Mettre à jour",
  dismissLabel: "Cacher",
};
