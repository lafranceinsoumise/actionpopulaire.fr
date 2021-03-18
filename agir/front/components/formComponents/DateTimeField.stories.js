import React from "react";

import DateTimeField from "./DateTimeField";

export default {
  component: DateTimeField,
  title: "Form/DateTimeField",
  argTypes: {
    onChange: { table: { disable: true } },
  },
};

const Template = (args) => {
  const [value, setValue] = React.useState(args.value);
  const handleChange = React.useCallback((datetime) => {
    setValue(datetime);
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
      <DateTimeField {...args} value={value} onChange={handleChange} />
      <pre>Value : {value ? <strong>{value}</strong> : <em>empty</em>}</pre>
      <button onClick={() => setValue(args.value)}>Reset</button>
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  value: "",
  id: "field",
  label: "Date de naissance",
  error: "",
  disabled: false,
};

export const DateOnly = Template.bind({});
DateOnly.args = {
  ...Default.args,
  type: "date",
};

export const TimeOnly = Template.bind({});
TimeOnly.args = {
  ...Default.args,
  type: "time",
};

export const DateTime = Template.bind({});
DateTime.args = {
  ...Default.args,
  type: "datetime",
};

export const Filled = Template.bind({});
Filled.args = {
  ...Default.args,
  value: "2021-01-06 23:59:00",
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
