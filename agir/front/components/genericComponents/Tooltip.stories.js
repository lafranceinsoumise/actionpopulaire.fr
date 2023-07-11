import React from "react";

import Tooltip from "./Tooltip";

export default {
  component: Tooltip,
  title: "Generic/Tooltip",
};

const Template = (args) => (
  <div
    style={{
      position: "fixed",
      top: "50%",
      left: "50%",
      width: 53,
      height: 53,
      background:
        "radial-gradient(dodgerblue, transparent, dodgerblue, transparent, dodgerblue, transparent, dodgerblue, transparent, dodgerblue, transparent, dodgerblue)",
      borderRadius: "100%",
    }}
  >
    <Tooltip {...args} onClose={args.hasCloseButton ? debug : undefined} />
  </div>
);

export const TopLeft = Template.bind({});
TopLeft.args = {
  hasCloseButton: true,
  position: "top-left",
  shouldShow: true,
  children: "Hello!",
};

export const TopRight = Template.bind({});
TopRight.args = {
  hasCloseButton: true,
  position: "top-right",
  shouldShow: true,
  children: "Hello!",
};

export const TopCenter = Template.bind({});
TopCenter.args = {
  hasCloseButton: true,
  position: "top-center",
  shouldShow: true,
  children: "Hello!",
};
