import React from "react";

import Footer from "./Footer";

export default {
  component: Footer,
  title: "Dashboard/Footer",
};

const Template = (args, { globals }) => (
  <Footer hasBanner={globals.auth !== "authenticated"} {...args} />
);

export const Default = Template.bind({});
Default.args = {};
