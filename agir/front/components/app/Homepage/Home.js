import React from "react";

import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import Footer from "@agir/front/dashboardComponents/Footer";

import MobileHome from "./MobileHome";
import DesktopHome from "./DesktopHome";

const Home = (props) => (
  <>
    <ResponsiveLayout
      MobileLayout={MobileHome}
      DesktopLayout={DesktopHome}
      {...props}
    />
    <Footer hideBanner />
  </>
);

export default Home;
