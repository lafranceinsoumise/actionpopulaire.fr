import React from "react";

import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";
import MapPage from "./MapPage";

export default {
  component: MapPage,
  title: "Map/MapPage",
};

const Template = (args) => {
  return (
    <TestGlobalContextProvider value={{ routes: args.routes }}>
      <div
        style={{
          backgroundColor: "#e4e4e4",
          minWidth: "100vw",
          minHeight: "100vh",
        }}
      >
        <MapPage {...args} user={args.hasUser ? {} : null} />
      </div>
    </TestGlobalContextProvider>
  );
};

export const Default = Template.bind({});
Default.args = {
  hasUser: true,
  type: "groups",
  backRoute: "back",
  createRoute: "create",
  map: "https://agir.lafranceinsoumise.fr/carte/groupes",
  routes: {
    back: "#back",
    create: "#create",
  },
};
