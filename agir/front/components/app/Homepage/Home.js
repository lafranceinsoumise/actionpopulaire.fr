import React from "react";

import IntroApp from "@agir/front/app/IntroApp";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";

import { useMobileApp } from "@agir/front/app/hooks";

import MobileHome from "./MobileHome";
import DesktopHome from "./DesktopHome";

const Home = (props) => {
  const { isMobileApp } = useMobileApp();

  if (isMobileApp) {
    return <IntroApp />;
  }

  return (
    <ResponsiveLayout
      MobileLayout={MobileHome}
      DesktopLayout={DesktopHome}
      {...props}
    />
  );
};

export default Home;
