import React from "react";

import Button from "./Button";

export default {
  component: Button,
  title: "Button",
};

const Template = (args) => <Button {...args} />;

export const PrimaryColor = Template.bind({});
PrimaryColor.args = {
  children: "Voir le groupe",
  color: "primary",
};

export const SecondaryColor = Template.bind({});
SecondaryColor.args = {
  children: "Participer à l'événement",
  color: "secondary",
};

export const Default = Template.bind({});
Default.args = { children: "Modifier" };

export const Small = Template.bind({});
Small.args = { children: "Petit bouton", small: true };

export const Disabled = Template.bind({});
Disabled.args = { children: "Désactivé", disabled: true };
