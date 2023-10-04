import React from "react";

import RadioListField from "./RadioListField";

export default {
  component: RadioListField,
  title: "Form/RadioListField",
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

  return <RadioListField {...args} value={value} onChange={handleChange} />;
};

export const Default = Template.bind({});
Default.args = {
  value: false,
  id: "attachment",
  label: "Type de pièce jointe",
  disabled: false,
  options: [
    { value: "E", label: "Devis" },
    { value: "I", label: "Facture" },
    { value: "B", label: "Impression" },
    {
      value: "P",
      label: "Photo ou illustration de l'événement, de la salle, du matériel",
    },
    { value: "O", label: "Autre type de justificatif" },
  ],
};

export const Unchecked = Template.bind({});
Unchecked.args = {
  ...Default.args,
  value: undefined,
};

export const Checked = Template.bind({});
Checked.args = {
  ...Default.args,
  value: "E",
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Default.args,
  disabled: true,
};

export const DisabledChecked = Template.bind({});
DisabledChecked.args = {
  ...Checked.args,
  disabled: true,
};
