import React from "react";

import groupData from "@agir/front/mockData/groups";

import { Container } from "@agir/front/genericComponents/grid";
import GroupSuggestions from "./GroupSuggestions";

export default {
  component: GroupSuggestions,
  title: "Groupes/GroupSuggestions",
};

const Template = (args) => (
  <Container style={{ minHeight: "100vh" }}>
    <GroupSuggestions {...args} />
  </Container>
);

export const WithoutSuggestions = Template.bind({});
WithoutSuggestions.args = {
  groups: [],
};

export const WithSuggestions = Template.bind({});
WithSuggestions.args = {
  groups: groupData.filter((group) => !group.isMember),
};
