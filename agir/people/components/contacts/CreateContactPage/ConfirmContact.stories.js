import React from "react";

import ConfirmContact from "./ConfirmContact";

export default {
  component: ConfirmContact,
  title: "CreateContactPage/ConfirmContact",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <ConfirmContact {...args} />;

export const Default = Template.bind({});
Default.args = {
  data: {
    firstName: "Foo",
    lastName: "Bar",
    zip: "75010",
    email: "foo@bar.com",
    phone: "06 00 00 00 00",
    nl2022_exceptionnel: true,
    nl2022: true,
    isGroupFollower: true,
    isLiaison: true,
    address: "25 passage Dubail",
    city: "Paris",
    country: "FR",
  },
};
