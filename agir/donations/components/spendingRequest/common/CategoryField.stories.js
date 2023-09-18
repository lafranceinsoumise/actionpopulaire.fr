import React from "react";

import CategoryField from "./CategoryField";
import { CATEGORY_OPTIONS } from "./form.config";

export default {
  component: CategoryField,
  title: "Donations/SpendingRequest/CategoryField",
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

  return <CategoryField {...args} value={value} onChange={handleChange} />;
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
  value: Object.values(CATEGORY_OPTIONS)[3].value,
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
