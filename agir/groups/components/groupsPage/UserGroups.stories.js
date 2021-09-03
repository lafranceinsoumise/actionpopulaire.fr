import React from "react";

import groupData from "@agir/front/mockData/groups";

import { Container } from "@agir/front/genericComponents/grid";
import UserGroups from "./UserGroups";

export default {
  component: UserGroups,
  title: "Groupes/UserGroups",
};

const Template = (args) => (
  <Container style={{ minHeight: "100vh" }}>
    <UserGroups {...args} />
  </Container>
);

export const Default = Template.bind({});
Default.args = {
  groups: [
    ...groupData.filter((group) => group.isActiveMember).slice(0, 3),
    ...groupData
      .filter((group) => group.isMember && !group.isActiveMember)
      .slice(0, 3),
  ],
};
