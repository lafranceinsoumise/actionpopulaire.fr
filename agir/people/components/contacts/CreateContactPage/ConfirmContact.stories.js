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
    is2022: true,
    newsletters: ["2022", "2022_exceptionnel", "2022_liaison"],
    group: {
      id: "a1a1",
      value: "a1a1a",
      label: "Nom du groupe",
      name: "Nom du groupe",
    },
    hasGroupNotifications: true,
    address: "25 passage Dubail",
    city: "Paris",
    country: "FR",
  },
};
