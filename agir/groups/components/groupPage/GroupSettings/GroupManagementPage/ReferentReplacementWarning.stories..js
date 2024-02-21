import React from "react";

import MOCK_GROUP from "@agir/front/mockData/group";
import ReferentReplacementWarning from "./ReferentReplacementWarning";

export default {
  component: ReferentReplacementWarning,
  title: "GroupSettings/ReferentReplacementWarning",
};

const Template = (args) => <ReferentReplacementWarning {...args} />;

export const Default = Template.bind({});
Default.args = {
  group: MOCK_GROUP,
};
