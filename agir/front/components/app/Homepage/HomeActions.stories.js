import React from "react";

import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";

import HomeActions from "./HomeActions";

export default {
  component: HomeActions,
  title: "app/Home/Actions",
};

const Template = (args) => (
  <TestGlobalContextProvider value={{ routes: {} }}>
    <HomeActions {...args} />
  </TestGlobalContextProvider>
);
export const Default = Template.bind({});
Default.args = {};
