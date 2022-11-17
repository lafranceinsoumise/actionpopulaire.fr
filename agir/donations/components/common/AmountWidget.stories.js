import React from "react";

import CONFIG from "@agir/donations/common/config";
import { Theme } from "@agir/donations/common/StyledComponents";
import AmountWidget from "@agir/donations/common/AmountWidget";

export default {
  component: AmountWidget,
  title: "Donations/AmountWidget",
  parameters: {
    layout: "padded",
  },
  argTypes: {
    theme: {
      options: Object.keys(CONFIG),
      control: { type: "radio" },
    },
  },
};

const Template = ({ theme, groupDonation, ...args }) => {
  const [amount, setAmount] = React.useState(0);
  const [groupPercentage, setGroupPercentage] = React.useState();
  const [byMonth, setByMonth] = React.useState(false);

  const handleChangeAmount = React.useCallback(
    (value) => {
      args.onChangeAmount(value);
      setAmount(value);
    },
    [args]
  );

  const handleChangeGroupPercentage = React.useCallback(
    (value) => {
      args.onChangeGroupPercentage(value);
      setGroupPercentage(value);
    },
    [args]
  );

  const handleChangeByMonth = React.useCallback(
    (value) => {
      args.onChangeByMonth(value);
      setByMonth(value);
    },
    [args]
  );

  return (
    <Theme type={theme}>
      <AmountWidget
        {...args}
        amount={amount}
        onChangeAmount={handleChangeAmount}
        groupPercentage={groupDonation ? groupPercentage : undefined}
        onChangeGroupPercentage={
          groupDonation ? handleChangeGroupPercentage : undefined
        }
        byMonth={byMonth}
        onChangeByMonth={handleChangeByMonth}
      />
    </Theme>
  );
};

export const Default = Template.bind({});
Default.args = {
  groupDonation: false,
  disabled: false,
  error: "",
  theme: "LFI",
};

export const WithGroupDonation = Template.bind({});
WithGroupDonation.args = {
  ...Default.args,
  groupDonation: true,
};
