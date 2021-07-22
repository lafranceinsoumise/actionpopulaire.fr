import React from "react";

import EmailList from "./EmailList.js";

export default {
  component: EmailList,
  title: "Generic/EmailList",
  parameters: {
    layout: "centered",
  },
};

const Template = (args) => <EmailList {...args} />;

export const Default = Template.bind({});
Default.args = {
  data: ["a@b.com", "c@d.com"],
};
