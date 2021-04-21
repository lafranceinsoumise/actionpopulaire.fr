import React from "react";

import AppStore from "./AppStore";

export default {
  component: AppStore,
  title: "Generic/AppStore",
};

const Template = (args) => {
  return (
    <div style={{ padding: "20px" }}>
      <AppStore {...args} />
    </div>
  );
};

export const Apple = Template.bind({});
Apple.args = {
  type: "apple",
};

export const Google = Template.bind({});
Google.args = {
  type: "google",
};
