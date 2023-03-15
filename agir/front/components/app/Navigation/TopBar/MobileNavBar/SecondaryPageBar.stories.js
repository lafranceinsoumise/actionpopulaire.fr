import React from "react";

import style from "@agir/front/genericComponents/_variables.scss";
import user from "@agir/front/mockData/user";

import SecondaryPageBar from "./SecondaryPageBar";

export default {
  component: SecondaryPageBar,
  title: "Navigation/TopBar/Mobile/Secondary page",
  parameters: {
    backgrounds: { default: "black50" },
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
      <SecondaryPageBar
        user={globals.auth === "authenticated" && user}
        {...args}
      />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  isLoading: false,
  title: "Page title !",
};

export const WithSettingsLink = Template.bind({});
WithSettingsLink.args = {
  title: "Page title !",
  settingsLink: {
    to: "/",
    label: "Settings",
  },
};
