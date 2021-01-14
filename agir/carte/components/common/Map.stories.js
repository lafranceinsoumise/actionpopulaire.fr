import React from "react";

import Map from "./Map";

export default {
  component: Map,
  title: "Map/Map",
};

const Template = (args) => {
  return (
    <div
      style={{
        width: "100vw",
        height: "100vh",
        padding: "20vh 20vw",
      }}
    >
      <Map {...args} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  center: [-97.14704, 49.8844],
};

export const Static = Template.bind({});
Static.args = {
  ...Default.args,
  isStatic: true,
};

export const WithIcon = Template.bind({});
WithIcon.args = {
  ...Default.args,
  iconConfiguration: {
    iconName: "users",
    color: "purple",
  },
};
