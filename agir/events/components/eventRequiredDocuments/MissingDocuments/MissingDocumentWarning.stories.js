import React from "react";

import MissingDocumentWarning from "./MissingDocumentWarning";

export default {
  component: MissingDocumentWarning,
  title: "Event Required Documents/Missing Documents/MissingDocumentWarning",
  argTypes: {
    limitDate: {
      control: "date",
    },
  },
};

const Template = (args) => (
  <div style={{ maxWidth: 660, width: "100%", margin: "32px auto" }}>
    <MissingDocumentWarning {...args} limitDate={args.limitDate.toString()} />
  </div>
);

export const Default = Template.bind({});
Default.args = {
  missingDocumentCount: 2,
  limitDate: new Date(),
};
