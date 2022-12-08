import React from "react";

import DepartementField from "./DepartementField";

export default {
  component: DepartementField,
  title: "Form/DepartementField",
  argTypes: {
    onChange: { table: { disable: true } },
  },
};

const Template = (args) => {
  const [value, setValue] = React.useState(args.value);
  const handleChange = React.useCallback((departement) => {
    setValue(departement);
  }, []);

  return (
    <div
      style={{
        boxSizing: "border-box",
        padding: "32px 16px",
        maxWidth: "480px",
        margin: "0 auto",
      }}
    >
      <DepartementField {...args} value={value} onChange={handleChange} />
      <pre>Value : {value ? <strong>{value}</strong> : <em>empty</em>}</pre>
    </div>
  );
};

export const Empty = Template.bind({});
Empty.args = {
  value: "",
  name: "departement",
  label: "Département",
  error: "",
  maxLength: undefined,
  disabled: false,
  textArea: false,
};

export const Filled = Template.bind({});
Filled.args = {
  ...Empty.args,
  value: "976",
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
