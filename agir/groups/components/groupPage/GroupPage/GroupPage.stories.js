import React from "react";

import group from "./group.json";
import GroupPage from "./GroupPage";

export default {
  component: GroupPage,
  title: "Group/GroupPage",
};

export const Default = () => {
  return <GroupPage group={group} groupSuggestions={[group, group, group]} />;
};
