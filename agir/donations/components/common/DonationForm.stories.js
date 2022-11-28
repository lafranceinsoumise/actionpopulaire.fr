import React from "react";

import { Theme } from "@agir/donations/common/StyledComponents";
import DonationForm from "@agir/donations/common/DonationForm";

import { INITIAL_DATA } from "./form.config";

export default {
  component: DonationForm,
  title: "Donations/DonationForm",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => (
  <Theme>
    <DonationForm {...args} />
  </Theme>
);

export const Default = Template.bind({});
Default.args = {
  formData: INITIAL_DATA,
};
