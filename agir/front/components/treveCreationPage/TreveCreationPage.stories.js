import React from "react";
import { TreveCreationPage } from "./TreveCreationPage";

export default {
  component: NotFoundPage,
  title: "Layout/TreveCreationPage",
};

const Template = (args) => <TreveCreationPage {...args} />;

export const Default = Template.bind({});
Default.args = { isTopBar: false };
