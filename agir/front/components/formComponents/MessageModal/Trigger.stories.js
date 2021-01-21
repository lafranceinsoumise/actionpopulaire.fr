import React from "react";

import Trigger from "./Trigger";

export default {
  component: Trigger,
  title: "Form/MessageModal/Trigger",
};

const user = {
  fullName: "Bill Murray",
  avatar: "https://www.fillmurray.com/200/200",
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
Default.args = {
  user,
  onClick: () => {},
};
