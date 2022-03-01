import React from "react";
import { ErrorPage } from "./ErrorPage";

export default {
  component: ErrorPage,
  title: "App/ErrorPage",
};

const Template = (args) => <ErrorPage {...args} />;

export const Default = Template.bind({});
Default.args = {};

export const WithMessage = Template.bind({});
WithMessage.args = {
  errorMessage: "errorMessage is not defined",
};
