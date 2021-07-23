import React from "react";

import SubtypePanel from "./SubtypePanel";

import subtypes from "@agir/front/mockData/eventSubtypes";

export default {
  component: SubtypePanel,
  title: "Events/SubtypePanel",
  parameters: {
    layout: "centered",
  },
};

const Template = (args) => {
  const [value, setValue] = React.useState(args.value);

  return (
    <div style={{ minWidth: 372 }}>
      <SubtypePanel {...args} value={value} onChange={setValue} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  options: subtypes,
  shouldShow: true,
};
