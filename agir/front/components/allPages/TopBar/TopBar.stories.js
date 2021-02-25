import React from "react";
import TopBar from "./TopBar";

export default {
  component: TopBar,
  title: "Layout/TopBar",
};

const Template = ({ loggedIn, displayName, isInsoumise }) => (
  <TopBar user={loggedIn ? { displayName, isInsoumise } : null} />
);

export const Default = Template.bind({});
Default.args = {
  loggedIn: false,
  displayName: "Arthur",
  isInsoumise: true,
};
Default.argTypes = {
  user: { table: { disable: true } },
  routes: { table: { disable: true } },
};
