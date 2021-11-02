import React from "react";

import group from "@agir/front/mockData/group.json";

import JoinGroupDialog from "./JoinGroupDialog";

export default {
  component: JoinGroupDialog,
  title: "Group/GroupUserActions/JoinGroupDialog",
};

const Template = (args) => {
  return <JoinGroupDialog {...args} />;
};

export const Step1 = Template.bind({});
Step1.args = {
  step: 1,
  isLoading: false,
  personName: "Jane Doe",
  groupName: group.name,
  groupContact: group.contact,
  groupReferents: group.referents,
};
export const Step2 = Template.bind({});
Step2.args = {
  ...Step1.args,
  step: 2,
};
export const Step3 = Template.bind({});
Step3.args = {
  ...Step1.args,
  step: 3,
};
