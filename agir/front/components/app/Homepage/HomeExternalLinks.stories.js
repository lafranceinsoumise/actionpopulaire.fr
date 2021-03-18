import React from "react";

import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";

import HomeExternalLinks from "./HomeExternalLinks";

export default {
  component: HomeExternalLinks,
  title: "app/Home/ExternalLinks",
};

const Template = (args) => (
  <TestGlobalContextProvider value={{ routes: {} }}>
    <HomeExternalLinks {...args} />
  </TestGlobalContextProvider>
);
export const Default = Template.bind({});
Default.args = {};
