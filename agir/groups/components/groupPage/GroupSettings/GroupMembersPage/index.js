import React from "react";

import MembershipPanel from "@agir/groups/groupPage/GroupSettings/MembershipPanel";

import MainPanel from "./MainPanel";

const GroupMembersPage = (props) => (
  <MembershipPanel MainPanel={MainPanel} {...props} />
);

export default GroupMembersPage;
