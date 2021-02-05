import React from "react";

import group from "@agir/groups/groupPage/group.json";
import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";

import GroupOrders from "./GroupOrders";

export default {
  component: GroupOrders,
  title: "Group/GroupOrders",
};

const Template = (args) => {
  return (
    <TestGlobalContextProvider value={{ routes: { materiel: "#materiel" } }}>
      <GroupOrders {...args} />
    </TestGlobalContextProvider>
  );
};

export const Default = Template.bind({});
Default.args = {
  ...group,
};
