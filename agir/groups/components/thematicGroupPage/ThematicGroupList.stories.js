import React from "react";

import MOCK_GROUPS from "@agir/front/mockData/thematicGroups";
import ThematicGroupList from "./ThematicGroupList";

export default {
  component: ThematicGroupList,
  title: "Generic/ThematicGroupList",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <ThematicGroupList {...args} />;

export const Default = Template.bind({});
Default.args = {
  groups: MOCK_GROUPS,
};

export const Empty = Template.bind({});
Empty.args = {
  ...Default.args,
  groups: [],
};
