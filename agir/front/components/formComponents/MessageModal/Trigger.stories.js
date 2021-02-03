import React from "react";

import Trigger from "./Trigger";

export default {
  component: Trigger,
  title: "Form/MessageModal/Trigger",
};

const Template = (args) => {
  return (
    <div
      style={{
        padding: "16px",
        maxWidth: "648px",
        margin: "0 auto",
      }}
    >
      <Trigger {...args} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {};
