import React from "react";

import { Theme } from "@agir/donations/common/StyledComponents";
import AllocationWidget from "@agir/donations/common/AllocationWidget";
export default {
  component: AllocationWidget,
  title: "Donations/AllocationWidget",
  parameters: {
    layout: "padded",
  },
};

const Template = ({ onChange, ...args }) => {
  const [value, setValue] = React.useState();
  const handleChange = React.useCallback(
    (newValue) => {
      console.log(
        args.totalAmount,
        newValue.map((i) => i.value)
      );
      onChange(newValue);
      setValue(newValue);
    },
    [onChange]
  );

  return (
    <Theme type="LFI">
      <AllocationWidget {...args} value={value} onChange={handleChange} />
    </Theme>
  );
};

export const Default = Template.bind({});
Default.args = {
  totalAmount: 10050,
  disabled: false,
  groupId: "12345",
  fixedRatio: 0.2,
};

export const NoGroup = Template.bind({});
NoGroup.args = {
  ...Default.args,
  groupId: null,
};

export const NoCNS = Template.bind({});
NoCNS.args = {
  ...Default.args,
  fixedRatio: 0,
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Default.args,
  disabled: true,
};

export const WithError = Template.bind({});
WithError.args = {
  ...Default.args,
  error: "Merci de saisir une valeur valide",
};
