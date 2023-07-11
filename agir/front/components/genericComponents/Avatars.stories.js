import React from "react";

import Avatars from "./Avatars";

export default {
  component: Avatars,
  title: "Generic/Avatars",
  parameters: {
    layout: "centered",
  },
};

const Template = (args) => {
  return (
    <div
      style={{
        display: "inline-block",
        height: "auto",
        lineHeight: 0,
        padding: 0,
      }}
    >
      <Avatars {...args} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  people: [
    {
      id: "abc",
      displayName: "Jane Doe",
      image: `https://loremflickr.com/160/160/`,
    },
    {
      id: "cba",
      displayName: "John Doe",
      image: `https://loremflickr.com/161/161/`,
    },
  ],
};
