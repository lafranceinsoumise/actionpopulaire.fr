import React from "react";

import ActionCard from "./ActionCard";

export default {
  component: ActionCard,
  title: "Generic/ActionCard",
  argTypes: {
    onConfirm: { action: "onConfirm" },
    onDismiss: { action: "onDismiss" },
  },
};

const Template = (args) => {
  return (
    <div
      style={{
        maxWidth: 500,
        margin: "10px auto",
      }}
    >
      <ActionCard {...args} />
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
  dismissed: false,
  timestamp: new Date().toISOString(),
};
