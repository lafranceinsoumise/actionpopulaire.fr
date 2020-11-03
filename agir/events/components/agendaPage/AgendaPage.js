import React from "react";
import Layout from "@agir/front/dashboardComponents/Layout";
import Agenda from "@agir/events/agendaPage/Agenda";

const AgendaPage = (props) => (
  <Layout active="events">
    <Agenda {...props} />
  </Layout>
);

export default AgendaPage;

AgendaPage.propTypes = Agenda.propTypes;
