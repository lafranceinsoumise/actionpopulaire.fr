import React from "react";

import GroupFacts from "./GroupFacts";

export default {
  component: GroupFacts,
  title: "Group/GroupFacts",
  argTypes: {
    creationDate: {
      control: {
        type: "date",
      },
    },
    lastActivityDate: {
      control: {
        type: "date",
      },
    },
  },
};

const Template = (args) => {
  return <GroupFacts facts={args} />;
};

export const Default = Template.bind({});
Default.args = {
  eventCount: 5,
  activeMemberCount: 12,
  isCertified: true,
  creationDate: "2021-01-08 00:00:00",
  lastActivityDate: "2021-01-05 00:00:00",
};
