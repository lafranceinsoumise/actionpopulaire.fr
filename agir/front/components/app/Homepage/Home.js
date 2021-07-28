import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import Spacer from "@agir/front/genericComponents/Spacer";
import IntroApp from "@agir/front/app/IntroApp";
import Footer from "@agir/front/dashboardComponents/Footer";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import TopBar from "@agir/front/allPages/TopBar/TopBar";

import { useMobileApp, useDownloadBanner } from "@agir/front/app/hooks";

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
  const [isBannerDownload] = useDownloadBanner();

  if (isMobileApp) {
    return <IntroApp />;
  }

  return (
    <>
      <TopBar />
      {isBannerDownload && <Spacer size="80px" />}
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
