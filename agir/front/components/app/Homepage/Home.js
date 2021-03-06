import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import IntroApp from "@agir/front/app/IntroApp";
import Footer from "@agir/front/dashboardComponents/Footer";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import TopBar from "@agir/front/allPages/TopBar";

import { useMobileApp } from "@agir/front/app/hooks";

import MobileHome from "./MobileHome";
import DesktopHome from "./DesktopHome";

const StyledHome = styled.div`
  padding-top: 72px;

  @media (max-width: ${style.collapse}px) {
    padding-top: 56px;
  }
`;

const Home = (props) => {
  const { isMobileApp } = useMobileApp();

  if (isMobileApp) {
    return <IntroApp />;
  }

  return (
    <>
      <TopBar />
      <StyledHome>
        <ResponsiveLayout
          MobileLayout={MobileHome}
          DesktopLayout={DesktopHome}
          {...props}
        />
        <Footer hideBanner />
      </StyledHome>
    </>
  );
};

export default Home;
