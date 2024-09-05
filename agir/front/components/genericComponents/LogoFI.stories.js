import React from "react";

import LogoFI from "./LogoFI";

export default {
  component: LogoFI,
  title: "Generic/Logo FI",
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

const Template = (args) => <LogoFI {...args} />;

export const Default = Template.bind({});
Default.args = {
  alt: "La France insoumise",
  height: "auto",
  width: "100%",
};
