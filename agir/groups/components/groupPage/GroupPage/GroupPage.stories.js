import React from "react";

import group from "@agir/groups/groupPage/group.json";
import events from "@agir/groups/groupPage/events.json";
import messages from "@agir/groups/groupPage/messages.json";

import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";
import GROUP_PAGE_ROUTES from "./routes.config";

import GroupPage from "./GroupPage";

export default {
  component: GroupPage,
  title: "Group/GroupPage",
  argTypes: {
    activeTab: {
      control: {
        type: "select",
        options: GROUP_PAGE_ROUTES.map((t) => t.pathname),
      },
    },
  },
};

const Template = (args) => (
  <TestGlobalContextProvider value={{ csrfToken: "12345" }}>
    <div
      style={{
        background: "crimson",
        position: "sticky",
        zIndex: "999",
        top: 0,
        right: 0,
        left: 0,
        width: "100%",
        height: "72px",
      }}
    />
    <GroupPage {...args} />
  </TestGlobalContextProvider>
);

export const Default = Template.bind({});
Default.args = {
  user: {
    id: "bill",
    displayName: "Bill Murray",
  },
  isLoading: false,
  group: { ...group, isManager: false },
  groupSuggestions: [
    { ...group, id: "a" },
    { ...group, id: "b" },
    { ...group, id: "c" },
  ],
  upcomingEvents: events.slice(0, 1),
  allEvents: [...events],
  // pastEvents: events,
  activeTab: GROUP_PAGE_ROUTES[0].pathname,
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
  allEvents: [],
};
export const WithPastReports = Template.bind({});
WithPastReports.args = {
  ...Default.args,
  pastEventReports: events,
  activeTab: "comptes-rendus",
};
export const WithMessages = Template.bind({});
WithMessages.args = {
  ...Default.args,
  group: { ...group, isManager: true, isMember: true },
  pastEventReports: events,
  messages,
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
export const EmptyMemberView = Template.bind({});
EmptyMemberView.args = {
  ...Default.args,
  group: { ...group, isManager: false, isMember: true },
  upcomingEvents: [],
  pastEvents: [],
  allEvents: [],
  pastEventReports: [],
  messages: [],
};
export const EmptyManagerView = Template.bind({});
EmptyManagerView.args = {
  ...Default.args,
  group: { ...group, isManager: true, isMember: true },
  upcomingEvents: [],
  pastEvents: [],
  allEvents: [],
  pastEventReports: [],
  messages: [],
};
