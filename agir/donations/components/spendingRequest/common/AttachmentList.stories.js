import React from "react";

import AttachmentList from "./AttachmentList";

export default {
  component: AttachmentList,
  title: "Donations/SpendingRequest/AttachmentList",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <AttachmentList {...args} />;

export const Default = Template.bind({});
Default.args = {
  attachments: [
    {
      type: "I",
      title: "Le ticket de caisse",
      file: {
        name: "ticket.pdf",
      },
    },
    {
      type: "P",
      title: "Photo de la salle des fêtes",
      file: "https://loremflickr.com/255/130",
    },
  ],
  disabled: false,
};

export const Disabled = Template.bind({});
Disabled.args = {
  ...Default.args,
  disabled: true,
};
