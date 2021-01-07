import React from "react";

import SelectField from "./SelectField";

export default {
  component: SelectField,
  title: "Form/SelectField",
  argTypes: {
    onChange: { table: { disable: true } },
    children: { table: { disable: true } },
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
      <SelectField {...args} value={value} onChange={handleChange} />
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

const options = [
  { label: "Ocean", value: "#00B8D9" },
  { label: "Blue", value: "#0052CC" },
  { label: "Purple", value: "#5243AA" },
  { label: "Red", value: "#FF5630" },
  { label: "Orange", value: "#FF8B00" },
  { label: "Yellow", value: "#FFC400" },
  { label: "Green", value: "#36B37E" },
  { label: "Forest", value: "#00875A" },
  { label: "Slate", value: "#253858" },
  { label: "Silver", value: "#666666" },
];

export const Default = Template.bind({});
Default.args = {
  value: "",
  placeholder: "Choisir une couleur",
  type: "text",
  id: "color",
  label: "Couleur",
  error: "",
  disabled: false,
  options,
};

export const Empty = Default;

export const Filled = Template.bind({});
Filled.args = {
  ...Empty.args,
  value: options[0],
};

export const Multiple = Template.bind({});
Multiple.args = {
  ...Empty.args,
  isMulti: true,
};

export const Searchable = Template.bind({});
Searchable.args = {
  ...Empty.args,
  isSearchable: true,
};

export const Loading = Template.bind({});
Loading.args = {
  ...Filled.args,
  isLoading: true,
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
