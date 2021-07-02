import React from "react";

import OpenLayersMap from "./OpenLayersMap";

export default {
  component: OpenLayersMap,
  title: "OpenLayersMap/OpenLayersMap",
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
      <OpenLayersMap {...args} />
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
