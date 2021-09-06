import React from "react";

import GroupLinkForm from "./GroupLinkForm.js";

export default {
  component: GroupLinkForm,
  title: "GroupSettings/GroupLinks/GroupLinkForm",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <GroupLinkForm {...args} />;

export const Default = Template.bind({});
Default.args = {
  selectedLink: {},
  errors: null,
  isLoading: false,
};

export const Editing = Template.bind({});
Editing.args = {
  ...Default.args,
  selectedLink: {
    id: 15,
    label: "An old link",
    url: "https://actionpopulaire.fr",
  },
};

export const WithErrors = Template.bind({});
WithErrors.args = {
  ...Editing.args,
  errors: {
    label: "This does not mean anything!",
    url: "This is not an URL",
  },
};

export const Loading = Template.bind({});
Loading.args = {
  ...Editing.args,
  isLoading: true,
};
