import React from "react";

import Avatar from "./Avatar";

export default {
  component: Avatar,
  title: "Generic/Avatar",
};

const Template = (args) => {
  return (
    <div style={{ padding: "20px" }}>
      <Avatar {...args} />
    </div>
  );
};

export const WithoutImage = Template.bind({});
WithoutImage.args = {
  name: "John Doe",
  avatar: "",
};

export const WithImage = Template.bind({});
WithImage.args = {
  name: "John Doe",
  avatar: "https://www.fillmurray.com/200/200",
};
