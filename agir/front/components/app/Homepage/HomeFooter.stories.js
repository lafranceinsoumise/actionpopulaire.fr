import React from "react";

import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";

import HomeFooter from "./HomeFooter";

export default {
  component: HomeFooter,
  title: "app/Home/Footer",
};

const Template = (args) => (
  <TestGlobalContextProvider value={{ routes: {} }}>
    <HomeFooter {...args} />
  </TestGlobalContextProvider>
);
export const Default = Template.bind({});
Default.args = {};
