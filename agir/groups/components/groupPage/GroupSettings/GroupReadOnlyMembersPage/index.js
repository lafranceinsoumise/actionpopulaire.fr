import React from "react";

import { ReadOnlyMembershipPanel } from "@agir/groups/groupPage/GroupSettings/MembershipPanel";

import MainPanel from "./MainPanel";

const GroupReadOnlyMembersPage = (props) => (
  <ReadOnlyMembershipPanel MainPanel={MainPanel} {...props} />
);

export default GroupReadOnlyMembersPage;
