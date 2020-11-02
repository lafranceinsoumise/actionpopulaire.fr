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

const example = {
  "waiting-payment": {
    name: "waiting-payment",
    text:
      "Vous n'avez pas encore réglé votre place pour l'événément : {événement}",
    iconName: "alert-circle",
    confirmLabel: "Payer",
    dismissLabel: "Voir l'événement",
  },
  "group-invitation": {
    name: "group-invitation",
    text: "Vous avez été invité-e à rejoindre le groupe {groupe}",
    iconName: "mail",
    confirmLabel: "Rejoindre",
    dismissLabel: "Décliner",
  },
  "new-member": {
    name: "new-member",
    text:
      "{membre} a rejoint votre groupe {groupe} Prenez le temps de l’accueillir !",
    iconName: "user-plus",
    confirmLabel: "Copier le mail",
    dismissLabel: "C'est fait",
  },
  "waiting-location-group": {
    name: "waiting-location-group",
    text: "Précisez la localisation de votre groupe {groupe}",
    iconName: "alert-circle",
    confirmLabel: "Mettre à jour",
    dismissLabel: "Cacher",
  },
  "group-coorganization-invite": {
    name: "group-coorganization-invite",
    text:
      "{membre} a proposé à votre groupe {groupe} de co-organiser : {événement}",
    iconName: "mail",
    confirmLabel: "Voir",
    dismissLabel: "Décliner",
  },
  "waiting-location-event": {
    name: "waiting-location-event",
    text: "Précisez la localisation de votre événement : {événement}",
    iconName: "alert-circle",
    confirmLabel: "Mettre à jour",
    dismissLabel: "Cacher",
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

export const WaitingPayment = Template.bind({});
WaitingPayment.args = example["waiting-payment"];
export const GroupInvitation = Template.bind({});
GroupInvitation.args = example["group-invitation"];
export const NewMember = Template.bind({});
NewMember.args = example["new-member"];
export const WaitingLocationGroup = Template.bind({});
WaitingLocationGroup.args = example["waiting-location-group"];
export const GroupCoorganizationInvite = Template.bind({});
GroupCoorganizationInvite.args = example["group-coorganization-invite"];
export const WaitingLocationEvent = Template.bind({});
WaitingLocationEvent.args = example["waiting-location-event"];
