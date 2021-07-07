import React from "react";

import StaticMap from "./StaticMap";

export default {
  component: StaticMap,
  title: "OpenLayersMap/StaticMap",
};

const Template = (args) => {
  return (
    <div
      style={{
        padding: 0,
        margin: 0,
        maxWidth: "992px",
        width: "100%",
        height: "300px",
      }}
    >
      <StaticMap {...args} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  staticMapUrl:
    "https://mwa-web-media.s3-eu-west-1.amazonaws.com/projects/mwa-web-frberfgoed-p/s3fs-public/artpiece/dig18106-z2rimuxdgwtviuedirbn9n30.jpg?inZbPb70vAcv5vWgVGVoHb9TMEbfRdf_",
  iconConfiguration: {
    iconName: "users",
    color: "magenta",
  },
};

export const NoConfig = Template.bind({});
NoConfig.args = {
  staticMapUrl:
    "https://mwa-web-media.s3-eu-west-1.amazonaws.com/projects/mwa-web-frberfgoed-p/s3fs-public/artpiece/dig18106-z2rimuxdgwtviuedirbn9n30.jpg?inZbPb70vAcv5vWgVGVoHb9TMEbfRdf_",
};
