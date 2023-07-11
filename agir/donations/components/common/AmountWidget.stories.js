import React from "react";

import CONFIG from "@agir/donations/common/config";
import { Theme } from "@agir/donations/common/StyledComponents";
import AmountWidget from "@agir/donations/common/AmountWidget";
import { MONTHLY_PAYMENT, SINGLE_TIME_PAYMENT } from "./form.config";

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

const Template = (args) => {
  const [amount, setAmount] = React.useState(0);
  const [allocations, setAllocations] = React.useState();
  const [paymentTiming, setPaymentTiming] = React.useState(
    args.allowedPaymentTimings[0],
  );

  const handleChangeAmount = React.useCallback(
    (value) => {
      args.onChangeAmount(value);
      setAmount(value);
    },
    [args],
  );

  const handleChangeAllocations = React.useCallback(
    (value) => {
      args.onChangeAllocations(value);
      setAllocations(value);
    },
    [args],
  );

  const handleChangePaymentTiming = React.useCallback(
    (value) => {
      args.onChangePaymentTiming(value);
      setPaymentTiming(value);
    },
    [args],
  );

  return (
    <Theme>
      <AmountWidget
        {...args}
        amount={amount}
        onChangeAmount={handleChangeAmount}
        allocations={allocations}
        onChangeAllocations={handleChangeAllocations}
        paymentTiming={paymentTiming}
        onChangePaymentTiming={handleChangePaymentTiming}
      />
    </Theme>
  );
};

export const Default = Template.bind({});
Default.args = {
  groupId: null,
  disabled: false,
  error: "",
  allowedPaymentTimings: [MONTHLY_PAYMENT, SINGLE_TIME_PAYMENT],
};

export const WithGroupDonation = Template.bind({});
WithGroupDonation.args = {
  ...Default.args,
  groupId: "12345",
};

export const WithFixedRatio = Template.bind({});
WithFixedRatio.args = {
  ...Default.args,
  fixedRatio: 0.5,
};

export const WithoutPaymentTimingChoice = Template.bind({});
WithoutPaymentTimingChoice.args = {
  ...Default.args,
  allowedPaymentTimings: [SINGLE_TIME_PAYMENT],
};
