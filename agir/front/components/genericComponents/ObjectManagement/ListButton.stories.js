import React from "react";

import { ButtonAddList } from "./ListButton";

export default {
  component: ButtonAddList,
  title: "GroupSettings/ButtonAddList",
};

const Template = (args) => <ButtonAddList {...args} />;

export const Default = Template.bind({});

Default.args = {
  label: "Ajouter votre binôme",
  onClick: () => {},
};

export const AddOrganizer = Template.bind({});

AddOrganizer.args = {
  label: "Ajouter un·e gestionnaire",
  onClick: () => {},
};
