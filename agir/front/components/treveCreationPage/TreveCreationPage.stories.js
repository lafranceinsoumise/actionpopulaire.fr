import React from "react";
import { TreveCreationPage } from "./TreveCreationPage";

export default {
  component: TreveCreationPage,
  title: "Layout/TreveCreationPage",
};

const Template = (args) => <TreveCreationPage {...args} />;

export const Default = Template.bind({});
Default.args = { hasTopBar: false };
