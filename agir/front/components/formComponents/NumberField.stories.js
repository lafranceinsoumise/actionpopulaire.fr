import React from "react";

import NumberField from "./NumberField";

export default {
  component: NumberField,
  title: "Form/NumberField",
  argTypes: {
    onChange: { table: { disable: true } },
    children: { table: { disable: true } },
  },
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => {
  const [value, setValue] = React.useState(args.value);
  const handleChange = React.useCallback((newValue) => {
    setValue(newValue);
  }, []);

  return (
    <>
      <NumberField {...args} value={value} onChange={handleChange} />
      <pre>Current value&nbsp;:&nbsp;{value}</pre>
    </>
  );
};

export const Empty = Template.bind({});
Empty.args = {
  value: "",
  type: "text",
  id: "field",
  label: "Montant",
  error: "",
  disabled: false,
  currency: true,
};

export const Filled = Template.bind({});
Filled.args = {
  ...Empty.args,
  value: 1500,
  currency: true,
  large: true,
};

export const WithHelpText = Template.bind({});
WithHelpText.args = {
  ...Filled.args,
  helpText: "Texte d'aide si necessaire",
};

export const Focused = Template.bind({});
Focused.args = {
  ...Filled.args,
  autoFocus: true,
};

export const WithValidationError = Template.bind({});
WithValidationError.args = {
  ...Filled.args,
  error: "Texte d’erreur sur le champ",
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Filled.args,
  disabled: true,
};
