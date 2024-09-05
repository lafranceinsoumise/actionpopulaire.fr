import React from "react";

import * as style from "@agir/front/genericComponents/_variables-light.scss";
import user from "@agir/front/mockData/user";
import DashboardPageBar from "./DashboardPageBar";

export default {
  component: DashboardPageBar,
  title: "Navigation/TopBar/Mobile/Dashboard page",
  parameters: {
    backgrounds: { default: "text50" },
  },
};

const Template = (args, { globals }) => {
  return (
    <div
      style={{
        width: "100%",
        margin: "auto",
        maxWidth: 992,
        height: 54,
        boxShadow: style.elaborateShadow,
      }}
    >
      <DashboardPageBar
        user={globals.auth === "authenticated" && user}
        {...args}
      />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  isLoading: false,
  settingsLink: null,
};

export const WithSettingsLink = Template.bind({});
WithSettingsLink.args = {
  ...Default.args,
  settingsLink: {
    to: "/",
    label: "Settings",
  },
};
