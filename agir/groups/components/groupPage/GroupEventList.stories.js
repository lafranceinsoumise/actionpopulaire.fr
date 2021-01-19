import React from "react";

import GroupEventList from "./GroupEventList";

import events from "./GroupPage/events.json";

export default {
  component: GroupEventList,
  title: "Group/GroupEventList",
  argTypes: {
    loadMore: { action: "loadMorePastEvents" },
  },
};

const Template = ({ hasEvents, ...args }) => {
  return <GroupEventList {...args} events={hasEvents ? events : null} />;
};

export const Default = Template.bind({});
Default.args = {
  title: "Événements",
  hasEvents: true,
  isLoading: false,
  loadMore: undefined,
};

export const FirstLoading = Template.bind({});
FirstLoading.args = {
  title: "Événements",
  hasEvents: false,
};

export const withLoadMoreButton = Template.bind({});
withLoadMoreButton.args = {
  title: "Événements",
  hasEvents: true,
  isLoading: false,
};

export const LoadingMore = Template.bind({});
LoadingMore.args = {
  title: "Événements",
  hasEvents: true,
  isLoading: true,
};
