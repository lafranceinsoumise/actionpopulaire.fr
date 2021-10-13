import React from "react";

import ShareContentUrl from "./ShareContentUrl";

export default {
  component: ShareContentUrl,
  title: "Generic/ShareContentUrl",
};

const Template = (args) => <ShareContentUrl {...args} />;

export const Default = Template.bind({});
Default.args = {
  url: "https://actionpopulaire.fr",
};
