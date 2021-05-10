import React from "react";
import TopBar from "./TopBar";
import { useLocation } from "react-router-dom";

export default {
  component: TopBar,
  title: "Layout/TopBar",
};

const Template = ({ loggedIn, displayName, isInsoumise }) => (
  <TopBar
    path={useLocation().pathname}
    user={loggedIn ? { displayName, isInsoumise } : null}
  />
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
