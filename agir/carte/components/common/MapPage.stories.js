import React from "react";

import MapPage from "./MapPage";

export default {
  component: MapPage,
  title: "Map/MapPage",
};

const Template = (args) => {
  return (
    <div
      style={{
        backgroundColor: "#e4e4e4",
        minWidth: "100vw",
        minHeight: "100vh",
      }}
    >
      <MapPage {...args} user={args.hasUser ? {} : null} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  hasUser: true,
  type: "groups",
  back: "#back",
  create: "#create",
  map: "https://agir.lafranceinsoumise.fr/carte/groupes",
};
