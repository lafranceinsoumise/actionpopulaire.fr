import React from "react";

import CountryField from "./CountryField";

export default {
  component: CountryField,
  title: "Form/CountryField",
  argTypes: {
    onChange: { table: { disable: true } },
  },
};

const Template = (args) => {
  const [value, setValue] = React.useState(args.value);
  const handleChange = React.useCallback((country) => {
    setValue(country);
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
      <CountryField {...args} value={value} onChange={handleChange} />
      <pre>Value : {value ? <strong>{value}</strong> : <em>empty</em>}</pre>
    </div>
  );
};

export const Empty = Template.bind({});
Empty.args = {
  value: "",
  name: "country",
  label: "Pays",
  error: "",
  maxLength: undefined,
  disabled: false,
  textArea: false,
};

export const Filled = Template.bind({});
Filled.args = {
  ...Empty.args,
  value: "FR",
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
