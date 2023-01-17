import React from "react";
import MultiDateInput from "./MultiDateInput";

export default {
  component: MultiDateInput,
  title: "Form/MultiDateField/Input",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => {
  return <MultiDateInput {...args} />;
};

export const Default = Template.bind({});
Default.args = {
  id: "field",
  disabled: false,
  initialValue: "",
};

export const Filled = Template.bind({});
Filled.args = {
  ...Default.args,
  initialValue: "2023-01-06,2023-05-07",
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Filled.args,
  disabled: true,
};

export const MinMax = Template.bind({});
MinMax.args = {
  ...Default.args,
  minDate: "1871-03-18",
  maxDate: "1871-05-28",
};

export const MinMaxLength = Template.bind({});
MinMaxLength.args = {
  ...Default.args,
  helpText: "Les dates devront couvrir une période d'au moins deux semaines",
  minLength: 1,
  maxLength: 3,
};

export const WithError = Template.bind({});
WithError.args = {
  ...Filled.args,
  error: "Les dates choisies n'ont pas de sens !",
};
