import React from "react";

import IntroApp from "@agir/front/app/IntroApp";
import Footer from "@agir/front/dashboardComponents/Footer";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import TopBar from "@agir/front/allPages/TopBar";

import { useMobileApp } from "@agir/front/app/hooks";

import MobileHome from "./MobileHome";
import DesktopHome from "./DesktopHome";

const Home = (props) => {
  const { isMobileApp } = useMobileApp();

  if (isMobileApp) {
    return <IntroApp />;
  }

  return (
    <>
      <TopBar />
      <ResponsiveLayout
        MobileLayout={MobileHome}
        DesktopLayout={DesktopHome}
        {...props}
      />
      <Footer hideBanner />
    </>
  );
};

export default Home;
