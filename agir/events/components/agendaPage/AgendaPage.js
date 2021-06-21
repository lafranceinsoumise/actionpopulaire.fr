import { Helmet } from "react-helmet";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import Spacer from "@agir/front/genericComponents/Spacer";

import { useDownloadBanner } from "@agir/front/app/hooks.js";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getIsSessionLoaded } from "@agir/front/globalContext/reducers";

import Agenda from "@agir/events/agendaPage/Agenda";
import ConnectivityWarning from "@agir/front/app/ConnectivityWarning";
import Layout from "@agir/front/dashboardComponents/Layout";
import TellMorePage from "@agir/front/authentication/Connexion/TellMore/TellMorePage";
import TopBar from "@agir/front/allPages/TopBar";
import { useLocation } from "react-router-dom";

const StyledWrapper = styled.div`
  padding-top: 72px;

  @media (max-width: ${style.collapse}px) {
    padding-top: 56px;
  }
`;

const AgendaPage = (props) => {
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const path = useLocation().pathname;

  const [isBannerDownload, _] = useDownloadBanner();

  if (!isSessionLoaded) {
    return null;
  }

  return (
    <>
      <TopBar path={path} />
      <ConnectivityWarning hasTopBar />
      <TellMorePage />

      {isBannerDownload && <Spacer size="80px" />}

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
