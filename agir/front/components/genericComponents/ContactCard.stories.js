import React from "react";

import ContactCard from "./ContactCard";

export default {
  component: ContactCard,
  title: "Generic/ContactCard",
};

const Template = (args) => <ContactCard {...args} />;

export const Default = Template.bind({});
Default.args = {
  name: "Serge Machin",
  phone: "+33600000000",
  email: "sergemachin@example.com",
};
