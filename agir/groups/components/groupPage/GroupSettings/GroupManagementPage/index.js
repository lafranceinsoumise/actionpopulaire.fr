import React from "react";

import MembershipPanel from "@agir/groups/groupPage/GroupSettings/MembershipPanel";

import MainPanel from "./MainPanel";

const GroupActiveMembersPage = (props) => (
  <MembershipPanel {...props} MainPanel={MainPanel} unselectMemberAfterUpdate />
);

export default GroupActiveMembersPage;
