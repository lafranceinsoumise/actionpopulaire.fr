import React from "react";

import Button from "@agir/front/genericComponents/Button";
import Steps from "./Steps";

export default {
  component: Steps,
  title: "Generic/Steps",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => (
  <Steps {...args}>
    <div>Step 1</div>
    <div>Step 2</div>
    <div>Step 3</div>
    <div>Step 4</div>
  </Steps>
);

export const Default = Template.bind({});
Default.args = {
  title: "voter au nom d'un·ne citoyen·ne",
  onSubmit: null,
};

export const AsForm = Template.bind({});
AsForm.args = {
  ...Default.args,
  as: "form",
  title: "voter au nom d'un·ne citoyen·ne",
  onSubmit: (e) => {
    e.preventDefault();
    alert("C'est fini !");
  },
};
