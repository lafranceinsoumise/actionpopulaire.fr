import React from "react";

import group from "@agir/groups/groupPage/GroupPage/group.json";
import GroupUserActions from "./GroupUserActions";
import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";

export default {
  component: GroupUserActions,
  title: "Group/GroupUserActions",
};

const Template = (args) => {
  return (
    <TestGlobalContextProvider value={{ csrfToken: "12345" }}>
      <GroupUserActions {...args} />
    </TestGlobalContextProvider>
  );
};

export const Default = Template.bind({});
Default.args = {
  ...group,
  isMember: false,
  isManager: false,
};

export const MemberView = Template.bind({});
MemberView.args = {
  ...group,
  isMember: true,
  isManager: false,
};

export const ManagerView = Template.bind({});
ManagerView.args = {
  ...group,
  isMember: true,
  isManager: true,
};
