import React from "react";

import { DownloadApp } from "./DownloadApp.js";

export default {
  component: DownloadApp,
  title: "Generic/DownloadApp",
};

const Template = (args) => <DownloadApp {...args} />;

export const Default = Template.bind({});
Default.args = {};
