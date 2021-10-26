import PropTypes from "prop-types";
import React from "react";

import EventRequiredDocumentsPage from "@agir/events/eventRequiredDocuments/EventRequiredDocumentsPage";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel";
import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";

const EventDocuments = (props) => {
  const { onBack, eventPk } = props;
  return (
    <>
      <HeaderPanel onBack={onBack} />
      <StyledTitle>Documents de l'événement public</StyledTitle>
      <EventRequiredDocumentsPage eventPk={eventPk} embedded />
    </>
  );
};
EventDocuments.propTypes = {
  onBack: PropTypes.func,
  eventPk: PropTypes.string,
};
export default EventDocuments;
