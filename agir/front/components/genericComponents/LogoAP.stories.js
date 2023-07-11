import React from "react";

import LogoAP from "./LogoAP";

export default {
  component: LogoAP,
  title: "Generic/Logo Action Populaire",
  parameters: {
    layout: "padded",
  },
  decorators: [
    (story) => (
      <div
        style={{
          padding: 0,
          border: "1px solid black",
          display: "inline-block",
        }}
      >
        {story()}
      </div>
    ),
  ],
};

const Template = (args) => <LogoAP {...args} />;

export const Default = Template.bind({});
Default.args = {
  alt: "Action Populaire",
  height: "auto",
  width: "auto",
};
