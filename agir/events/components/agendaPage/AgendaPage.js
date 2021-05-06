import { Helmet } from "react-helmet";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import Spacer from "@agir/front/genericComponents/Spacer";

import { useIsDesktop } from "@agir/front/genericComponents/grid.js";
import { useMobileApp } from "@agir/front/app/hooks.js";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getIsConnected,
  getIsSessionLoaded,
  getIsBannerDownload,
} from "@agir/front/globalContext/reducers";

import Agenda from "@agir/events/agendaPage/Agenda";
import ConnectivityWarning from "@agir/front/app/ConnectivityWarning";
import Homepage from "@agir/front/app/Homepage/Home";
import Layout from "@agir/front/dashboardComponents/Layout";
import TellMorePage from "@agir/front/authentication/Connexion/TellMore/TellMorePage";
import TopBar from "@agir/front/allPages/TopBar";

const StyledWrapper = styled.div`
  padding-top: 72px;

  @media (max-width: ${style.collapse}px) {
    padding-top: 56px;
  }
`;

const AgendaPage = (props) => {
  const isConnected = useSelector(getIsConnected);
  const isSessionLoaded = useSelector(getIsSessionLoaded);

  const isDesktop = useIsDesktop();
  const { isMobileApp } = useMobileApp();
  const isBannerDownload = useSelector(getIsBannerDownload);

  if (!isSessionLoaded) {
    return null;
  }

  if (!isConnected) {
    return (
      <>
        <ConnectivityWarning hasTopBar={false} />
        <Homepage />
      </>
    );
  }

  return (
    <>
      <TopBar />
      <ConnectivityWarning hasTopBar />
      <TellMorePage />

      {!isMobileApp && !isDesktop && isBannerDownload && (
        <Spacer size="100px" />
      )}

      <StyledWrapper>
        <Layout active="events" smallBackgroundColor={style.black25} hasBanner>
          <Helmet>
            <title>Événements - Action populaire</title>
          </Helmet>
          <Agenda {...props} />
        </Layout>
      </StyledWrapper>
    </>
  );
};

export default AgendaPage;
