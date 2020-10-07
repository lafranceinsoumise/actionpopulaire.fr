import React from "react";

import LogoFI from "./LogoFI";

export default {
  component: LogoFI,
  title: "Logo FI",
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
  height: null,
  width: null,
  alt: "La France insoumise",
};
