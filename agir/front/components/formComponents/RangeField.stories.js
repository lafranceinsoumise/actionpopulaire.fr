import React from "react";

import RangeField from "./RangeField";

export default {
  component: RangeField,
  title: "Form/RangeField",
  argTypes: {
    onChange: { table: { disable: true } },
  },
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => {
  const [value, setValue] = React.useState(args.value);
  const handleChange = React.useCallback((value) => {
    setValue(value);
  }, []);

  return <RangeField {...args} value={value} onChange={handleChange} />;
};

export const Default = Template.bind({});
Default.args = {
  id: "range",
  label: "Proposer des événements dans un rayon de :",
  min: 1,
  max: 500,
};

export const WithHelp = Template.bind({});
WithHelp.args = {
  ...Default.args,
  helpText: "Veuillez choisir une valeur entre 0 et 500",
};

export const WithValue = Template.bind({});
WithValue.args = {
  ...Default.args,
  value: 100,
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...WithValue.args,
  disabled: true,
};

export const WithError = Template.bind({});
WithError.args = {
  ...WithValue.args,
  error: "Vous vous êtes trompé !",
};
