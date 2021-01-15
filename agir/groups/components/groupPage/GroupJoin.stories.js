import React from "react";

import GroupJoin from "./GroupJoin";
import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";

export default {
  component: GroupJoin,
  title: "Group/GroupJoin",
};

const Template = (args) => {
  return (
    <TestGlobalContextProvider>
      <GroupJoin {...args} />
    </TestGlobalContextProvider>
  );
};

export const Default = Template.bind({});
Default.args = {
  url: "#join",
  is2022: false,
};
