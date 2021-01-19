import React from "react";

import group from "./group.json";
import events from "./events.json";

import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";
import GROUP_PAGE_TABS from "./tabs.config";

import GroupPage from "./GroupPage";

export default {
  component: GroupPage,
  title: "Group/GroupPage",
  argTypes: {
    activeTab: {
      control: {
        type: "select",
        options: GROUP_PAGE_TABS.map((t) => t.slug),
      },
    },
  },
};

const Template = (args) => (
  <TestGlobalContextProvider value={{ csrfToken: "12345" }}>
    <GroupPage {...args} />
  </TestGlobalContextProvider>
);

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
  activeTab: GROUP_PAGE_TABS[0].slug,
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
export const WithPastReports = Template.bind({});
WithPastReports.args = {
  ...Default.args,
  pastEventReports: events,
  activeTab: "comptes-rendus",
};
export const NonMemberView = Template.bind({});
NonMemberView.args = {
  ...Default.args,
  group: { ...group, isManager: false, isMember: false },
};
export const MemberView = Template.bind({});
MemberView.args = {
  ...Default.args,
  group: { ...group, isManager: false, isMember: true },
};
export const ManagerView = Template.bind({});
ManagerView.args = {
  ...Default.args,
  group: { ...group, isManager: true, isMember: true },
};
