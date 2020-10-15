import React from "react";

import Contact from "./Contact";

export default {
  component: Contact,
  title: "Generic/Contact",
};

const Template = (args) => <Contact {...args} />;

export const Default = Template.bind({});
Default.args = {
  name: "Serge Machin",
  phone: "+33600000000",
  email: "sergemachin@example.com",
};
