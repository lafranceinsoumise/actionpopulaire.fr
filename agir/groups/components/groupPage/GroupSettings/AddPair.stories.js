import React from "react";

import AddPair from "./AddPair.js";

export default {
  component: AddPair,
  title: "Group/AddPair",
};

const Template = (args) => <AddPair {...args} />;

export const Default = Template.bind({});

Default.args = {
  label: "Ajouter votre binôme",
  onClick: () =>{}
};

export const AddOrganizer = Template.bind({});

AddOrganizer.args = {
  label: "Ajouter un·e gestionnaire",
  onClick: () =>{},
  test: "lol"
};

