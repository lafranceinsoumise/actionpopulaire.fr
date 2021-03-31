import React from "react";

import RichTextField from "./RichTextField";

export default {
  component: RichTextField,
  title: "Form/RichTextField",
  argTypes: {
    onChange: { table: { disable: true } },
  },
};

const Template = (args) => {
  const [value, setValue] = React.useState(args.value);
  const handleChange = React.useCallback((value) => {
    setValue(value);
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
      <RichTextField {...args} value={value} onChange={handleChange} />
      <pre>
        Value:{" "}
        {value ? (
          <strong>{JSON.stringify(value, null, "\r  ")}</strong>
        ) : (
          <em>empty</em>
        )}
      </pre>
    </div>
  );
};

export const Empty = Template.bind({});
Empty.args = {
  value: "",
  id: "field",
  label: "Texte",
  error: "",
  disabled: false,
  placeholder: "Rich text",
};

export const Filled = Template.bind({});
Filled.args = {
  ...Empty.args,
  value: "Hello world!",
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
