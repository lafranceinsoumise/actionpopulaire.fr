import React from "react";
import { NotFoundPage } from "./NotFoundPage";

export default {
  component: NotFoundPage,
  title: "Layout/NotFoundPage",
};

const Template = (args) => <NotFoundPage {...args} />;

export const Default = Template.bind({});
Default.args = { hasTopBar: false };
