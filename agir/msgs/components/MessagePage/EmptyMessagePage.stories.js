import React from "react";

import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";

import EmptyMessagePage from "./EmptyMessagePage";

export default {
  component: EmptyMessagePage,
  title: "Messages/MessagePage/EmptyMessagePage",
};

const Template = (args) => {
  return (
    <TestGlobalContextProvider>
      <EmptyMessagePage {...args} />
    </TestGlobalContextProvider>
  );
};

export const Default = Template.bind({});
Default.args = {};
