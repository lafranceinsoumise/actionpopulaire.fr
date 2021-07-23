import PropTypes from "prop-types";
import React, { useState, useEffect } from "react";
import useSWR from "swr";

import * as api from "@agir/events/common/api";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer.js";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents.js";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel.js";

const EventCancelation = (props) => {
  const { onBack, illustration, eventPk } = props;

  const { data: event, mutate } = useSWR(
    api.getEventEndpoint("getEvent", { eventPk })
  );

  const [isLoading, setIsLoading] = useState(false);

  const handleQuit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    let error = "";
    try {
      const response = await api.quitEvent(id);
      if (response.error) {
        error = response.error;
      }
    } catch (err) {
      error = err.message;
    }
    setIsLoading(false);
    setIsQuitting(false);
    if (error) {
      log.error(error);
      return;
    }
    mutate(api.getEventEndpoint("getEvent", { eventPk: id }), (event) => ({
      ...event,
      rsvped: false,
    }));
  };

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Annuler l'événement</StyledTitle>

      <Spacer size="1rem" />

      <p>
        Voulez-vous annuler votre événement <strong>{event.name}</strong> ?
      </p>
      <p>
        Tous les participant·es recevront une notification leur indiquant que
        vous avez annulé l’événement.
      </p>
      <p>Cette action est irréversible.</p>

      <Spacer size="1rem" />
      <Button color="danger" onClick={handleQuit} disabled={isLoading}>
        Annuler l'événement
      </Button>
    </>
  );
};
EventCancelation.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  eventPk: PropTypes.string,
};
export default EventCancelation;
