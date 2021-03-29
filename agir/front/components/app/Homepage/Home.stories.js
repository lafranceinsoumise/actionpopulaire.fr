import React from "react";

import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";

import Home from "./Home";

export default {
  component: Home,
  title: "app/Home",
};

const Template = (args) => (
  <TestGlobalContextProvider
    value={{
      routes: { eventsMap: "https://actionpopulaire.fr/carte/evenements/" },
    }}
  >
    <Home {...args} />
  </TestGlobalContextProvider>
);
export const Default = Template.bind({});
Default.args = {};
