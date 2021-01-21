import React from "react";

import AnimatedMoreHorizontal from "./AnimatedMoreHorizontal";

export default {
  component: AnimatedMoreHorizontal,
  title: "Generic/AnimatedMoreHorizontal",
};

const Template = (args) => {
  return (
    <div style={{ padding: "20px" }}>
      <AnimatedMoreHorizontal {...args} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {};
