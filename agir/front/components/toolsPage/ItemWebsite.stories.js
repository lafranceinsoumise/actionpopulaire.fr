import React from "react";

import { ItemWebsite, WEBSITES } from "./ToolsPage";

export default {
  component: ItemWebsite,
  title: "Dashboard/PageTools/ItemWebsite",
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
      <ItemWebsite {...args} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  ...WEBSITES[0],
};
