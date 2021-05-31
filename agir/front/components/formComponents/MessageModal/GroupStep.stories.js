import React from "react";

import group from "@agir/front/mockData/group";

import GroupStep from "./GroupStep";

export default {
  component: GroupStep,
  title: "Form/MessageModal/GroupStep",
};

const Template = (args) => {
  return (
    <div
      style={{
        margin: "0 auto",
        width: "100%",
        maxWidth: "648px",
      }}
    >
      <GroupStep {...args} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  groups: [
    group,
    { ...group, id: group.id + "1" },
    { ...group, id: group.id + "2" },
  ],
};
