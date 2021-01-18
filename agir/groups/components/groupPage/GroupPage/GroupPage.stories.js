import React from "react";

import group from "./group.json";
import events from "./events.json";
import GroupPage from "./GroupPage";

export default {
  component: GroupPage,
  title: "Group/GroupPage",
};

const Template = (args) => <GroupPage {...args} />;

export const Default = Template.bind({});
Default.args = {
  isLoading: false,
  group: { ...group, isManager: false },
  groupSuggestions: [
    { ...group, id: "a" },
    { ...group, id: "b" },
    { ...group, id: "c" },
  ],
  upcomingEvents: events,
  pastEvents: events,
};
export const Loading = Template.bind({});
Loading.args = {
  ...Default.args,
  isLoading: true,
};
export const NoEvents = Template.bind({});
NoEvents.args = {
  ...Default.args,
  upcomingEvents: [],
  pastEvents: [],
};
export const ManagerView = Template.bind({});
ManagerView.args = {
  ...ManagerView.args,
  group: { ...group, isManager: true },
};
