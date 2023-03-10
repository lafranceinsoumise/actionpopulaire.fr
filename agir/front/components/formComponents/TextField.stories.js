import React from "react";

import TextField from "./TextField";

export default {
  component: TextField,
  title: "Form/TextField",
  argTypes: {
    onChange: { table: { disable: true } },
    children: { table: { disable: true } },
  },
};

const Template = (args) => {
  const [value, setValue] = React.useState(args.value);
  const handleChange = React.useCallback((e) => {
    setValue(e.target.value);
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
      <TextField {...args} value={value} onChange={handleChange} />
    </div>
  );
};

export const Empty = Template.bind({});
Empty.args = {
  value: "",
  type: "text",
  id: "field",
  label: "Prénom",
  error: "",
  maxLength: undefined,
  disabled: false,
  textArea: false,
};

export const Filled = Template.bind({});
Filled.args = {
  ...Empty.args,
  value: "Agathe",
};

export const WithHelpText = Template.bind({});
WithHelpText.args = {
  ...Filled.args,
  helpText: "Texte d'aide si necessaire",
};

export const WithMaxLength = Template.bind({});
WithMaxLength.args = {
  ...Filled.args,
  maxLength: 20,
};

export const WithMaxLengthError = Template.bind({});
WithMaxLengthError.args = {
  ...Filled.args,
  value: "01234567891011121314151617181920",
  maxLength: 20,
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

export const WithValidationErrorAndMaxLength = Template.bind({});
WithValidationErrorAndMaxLength.args = {
  ...WithMaxLength.args,
  error: "Texte d’erreur sur le champ",
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Filled.args,
  disabled: true,
};

export const LongText = Template.bind({});
LongText.args = {
  ...Empty.args,
  value:
    "Justo sodales lectus mi ante eu ad eleifend ligula iaculis a porttitor sit a dis suspendisse mollis nunc a dignissim laoreet dictumst habitasse phasellus potenti",
  textArea: true,
};

export const DarkWithIcon = Template.bind({});
DarkWithIcon.args = {
  ...Empty.args,
  dark: true,
  icon: "search",
  placeholder: "Rechercher un événement",
};
