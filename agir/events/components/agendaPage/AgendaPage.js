import { Helmet } from "react-helmet";
import React from "react";

import Agenda from "@agir/events/agendaPage/Agenda";

const AgendaPage = (props) => (
  <>
    <Helmet>
      <title>Événements - Action populaire</title>
    </Helmet>
    <Agenda {...props} />
  </>
);

export default AgendaPage;

AgendaPage.propTypes = Agenda.propTypes;
