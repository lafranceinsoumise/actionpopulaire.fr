import { Helmet } from "react-helmet";
import React from "react";

import style from "@agir/front/genericComponents/_variables.scss";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getIsConnected,
  getIsSessionLoaded,
} from "@agir/front/globalContext/reducers";

import Layout from "@agir/front/dashboardComponents/Layout";
import Agenda from "@agir/events/agendaPage/Agenda";
import Homepage from "@agir/front/app/Homepage/Home";
import TellMorePage from "@agir/front/authentication/Connexion/TellMore/TellMorePage";
import TopBar from "@agir/front/allPages/TopBar";

const AgendaPage = (props) => {
  const isConnected = useSelector(getIsConnected);
  const isSessionLoaded = useSelector(getIsSessionLoaded);

  if (!isSessionLoaded) {
    return null;
  }

  if (!isConnected) {
    return <Homepage />;
  }

  return (
    <>
      <TopBar />
      <TellMorePage />
      <Layout active="events" smallBackgroundColor={style.black25} hasBanner>
        <Helmet>
          <title>Événements - Action populaire</title>
        </Helmet>
        <Agenda {...props} />
      </Layout>
    </>
  );
};

export default AgendaPage;
