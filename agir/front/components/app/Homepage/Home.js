import React from "react";

import { ResponsiveLayout } from "@agir/front/genericComponents/grid";

import MobileHome from "./MobileHome";
import DesktopHome from "./DesktopHome";

const Home = (props) => (
  <ResponsiveLayout
    MobileLayout={MobileHome}
    DesktopLayout={DesktopHome}
    {...props}
  />
);

export default Home;
