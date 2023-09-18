import React from "react";

import CheckboxField from "./CheckboxField";

export default {
  component: CheckboxField,
  title: "Form/CheckboxField",
  argTypes: {
    onChange: { table: { disable: true } },
  },
};

const Template = (args) => {
  const [value, setValue] = React.useState(args.value);
  const handleChange = React.useCallback((e) => {
    setValue(e.target.checked);
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
      <CheckboxField {...args} value={value} onChange={handleChange} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  value: false,
  id: "field",
  label: "J’accepte la charte",
  disabled: false,
};

export const Toggle = Template.bind({});
Toggle.args = {
  ...Default.args,
  toggle: true,
};

export const Unchecked = Template.bind({});
Unchecked.args = {
  ...Default.args,
  value: false,
};

export const Checked = Template.bind({});
Checked.args = {
  ...Default.args,
  value: true,
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

export const MultilineLabel = Template.bind({});
MultilineLabel.args = {
  ...Default.args,
  label: (
    <>
      Some
      <br />
      multiline
      <br />
      label
    </>
  ),
};
