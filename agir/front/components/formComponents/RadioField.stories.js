import React from "react";

import RadioField from "./RadioField";

export default {
  component: RadioField,
  title: "Form/RadioField",
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
      <RadioField {...args} value={value} onChange={handleChange} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  value: false,
  id: "field",
  label: "J’accepte la charte",
  disabled: false,
  options: [
    { label: "Oui", value: "1" },
    { label: "Non", value: "0" },
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
  value: "1",
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
