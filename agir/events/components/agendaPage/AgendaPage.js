import { Helmet } from "react-helmet";
import React from "react";

import style from "@agir/front/genericComponents/_variables.scss";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getIsSessionLoaded } from "@agir/front/globalContext/reducers";

import Agenda from "@agir/events/agendaPage/Agenda";
import Layout from "@agir/front/dashboardComponents/Layout";

const AgendaPage = (props) => {
  const isSessionLoaded = useSelector(getIsSessionLoaded);

  if (!isSessionLoaded) {
    return null;
  }

  return (
    <Layout active="events" smallBackgroundColor={style.black25} hasBanner>
      <Helmet>
        <title>Événements - Action populaire</title>
      </Helmet>
      <Agenda {...props} />
    </Layout>
  );
};

export default AgendaPage;
