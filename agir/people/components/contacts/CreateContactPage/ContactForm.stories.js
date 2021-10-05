import React from "react";

import ContactForm from "./ContactForm";

export default {
  component: ContactForm,
  title: "CreateContactPage/ContactForm",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <ContactForm {...args} />;

export const Default = Template.bind({});
Default.args = {
  isLoading: false,
  error: null,
  groups: [
    { id: "abc123", name: "Mon groupe" },
    { id: "123abc", name: "Mon autre groupe" },
  ],
};

export const WithoutGroup = Template.bind({});
WithoutGroup.args = {
  ...Default.args,
  groups: [],
};
