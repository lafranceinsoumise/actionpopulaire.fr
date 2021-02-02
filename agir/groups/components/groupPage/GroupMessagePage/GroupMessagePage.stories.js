import React from "react";

import group from "@agir/groups/groupPage/group.json";
import messages from "@agir/groups/groupPage/messages.json";

import GroupMessagePage from "./GroupMessagePage";
import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";

export default {
  component: GroupMessagePage,
  title: "Group/GroupMessagePage",
};

const Template = (args) => {
  return (
    <TestGlobalContextProvider
      value={{ backLink: { href: "back", label: "Retour à l'accueil" } }}
    >
      <GroupMessagePage {...args} />
    </TestGlobalContextProvider>
  );
};

export const Default = Template.bind({});
Default.args = {
  user: {
    id: "bill",
    displayName: "Bill Murray",
  },
  group,
  message: messages[0],
  groupURL: "#group",
  messageURL: "#message",
};
