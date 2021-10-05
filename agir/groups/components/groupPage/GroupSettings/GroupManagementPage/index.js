import React from "react";

import MembershipPanel from "@agir/groups/groupPage/GroupSettings/MembershipPanel";

import MainPanel from "./MainPanel";

const GroupMembersPage = (props) => (
  <MembershipPanel {...props} MainPanel={MainPanel} unselectMemberAfterUpdate />
);

export default GroupMembersPage;
