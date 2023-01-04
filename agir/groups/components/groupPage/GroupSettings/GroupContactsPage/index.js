import React from "react";

import MembershipPanel from "@agir/groups/groupPage/GroupSettings/MembershipPanel";

import MainPanel from "./MainPanel";

const GroupContactsPage = (props) => (
  <MembershipPanel MainPanel={MainPanel} {...props} />
);

export default GroupContactsPage;
