import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import Spacer from "@agir/front/genericComponents/Spacer";
import IntroApp from "@agir/front/app/IntroApp";
import Footer from "@agir/front/dashboardComponents/Footer";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import TopBar from "@agir/front/allPages/TopBar";

import { useMobileApp } from "@agir/front/app/hooks";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getIsBannerDownload } from "@agir/front/globalContext/reducers";
import { useIsDesktop } from "@agir/front/genericComponents/grid.js";

import MobileHome from "./MobileHome";
import DesktopHome from "./DesktopHome";

const StyledHome = styled.div`
  padding-top: 72px;

  @media (max-width: ${style.collapse}px) {
    padding-top: 56px;
  }
`;

const Home = (props) => {
  const isDesktop = useIsDesktop();
  const { isMobileApp } = useMobileApp();
  const isBannerDownload = useSelector(getIsBannerDownload);

  if (isMobileApp) {
    return <IntroApp />;
  }

  return (
    <>
      <TopBar />

      {!isMobileApp && !isDesktop && isBannerDownload && (
        <Spacer size="100px" />
      )}

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
