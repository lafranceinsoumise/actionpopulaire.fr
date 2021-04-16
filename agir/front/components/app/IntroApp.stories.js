import React from "react";

import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";
import IntroApp from "./IntroApp";

export default {
  component: IntroApp,
  title: "app/IntroApp",
};

const Template = (args) => (
  <TestGlobalContextProvider>
    <IntroApp {...args} />
  </TestGlobalContextProvider>
);

export const Default = Template.bind({});
Default.args = {};
