import React from "react";

import TypeRadioField from "./TypeRadioField";
import { TYPE_OPTIONS } from "./form.config";

export default {
  component: TypeRadioField,
  title: "Donations/SpendingRequest/TypeRadioField",
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

  return <TypeRadioField {...args} value={value} onChange={handleChange} />;
};

export const Default = Template.bind({});
Default.args = {
  value: false,
  id: "type",
  label: "Catégorie de dépense",
  disabled: false,
};

export const Unchecked = Template.bind({});
Unchecked.args = {
  ...Default.args,
  value: undefined,
};

export const Checked = Template.bind({});
Checked.args = {
  ...Default.args,
  value: Object.values(TYPE_OPTIONS)[3].value,
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

export const WithError = Template.bind({});
WithError.args = {
  ...Checked.args,
  error: "Veuillez choisir une catégorie",
};
