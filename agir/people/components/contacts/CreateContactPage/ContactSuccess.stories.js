import React from "react";

import ContactSuccess from "./ContactSuccess";

export default {
  component: ContactSuccess,
  title: "CreateContactPage/ContactSuccess",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <ContactSuccess {...args} />;

export const Default = Template.bind({});
Default.args = {
  user: {
    firstName: "Foo",
  },
  group: {
    name: "Belleville - Ménilmontant",
  },
};
