import React from "react";

import ShareLink from "./ShareLink";

export default {
  component: ShareLink,
  title: "Generic/ShareLink",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <ShareLink {...args} />;

export const Default = Template.bind({});
Default.args = {
  title: "Un lien facile à copier ci-dessous",
  label: "Partager c'est sympa !",
  url: "https://actionpopulaire.fr",
};

export const Primary = Template.bind({});
Primary.args = {
  ...Default.args,
  color: "primary",
};

export const Secondary = Template.bind({});
Secondary.args = {
  ...Default.args,
  color: "secondary",
};

export const NoLabelNoTitle = Template.bind({});
NoLabelNoTitle.args = {
  url: "https://actionpopulaire.fr",
};

export const Disabled = Template.bind({});
Disabled.args = {
  url: "",
};
