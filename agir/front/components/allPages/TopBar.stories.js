import React from "react";
import { PureTopBar } from "./TopBar";

export default {
  component: PureTopBar,
  title: "Layout/TopBar",
};

const Template = ({ loggedIn, displayName, isInsoumise }) => (
  <PureTopBar user={loggedIn ? { displayName, isInsoumise } : null} />
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
