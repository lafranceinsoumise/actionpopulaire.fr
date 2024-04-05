import PropTypes from "prop-types";
import React, { useState, useEffect } from "react";
import useSWR from "swr";

import * as style from "@agir/front/genericComponents/_variables.scss";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents.js";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel.js";
import OnlineUrlField from "@agir/events/createEventPage/EventForm/OnlineUrlField";
import Button from "@agir/front/genericComponents/Button";

import { useToast } from "@agir/front/globalContext/hooks.js";
import * as api from "@agir/events/common/api";

const EventVisio = (props) => {
  const { onBack, illustration, eventPk } = props;

  const { data: event, mutate } = useSWR(
    api.getEventEndpoint("getEvent", { eventPk }),
  );

  const sendToast = useToast();
  const [onlineUrl, setOnlineUrl] = useState("");
  const [errors, setErrors] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setOnlineUrl(event.onlineUrl);
  }, [event]);

  const updateValue = (_, value) => {
    setOnlineUrl(value);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    setErrors({});
    setIsLoading(true);
    const res = await api.updateEvent(eventPk, { onlineUrl });
    setIsLoading(false);
    if (res.error) {
      setErrors(res.error);
      sendToast(
        res.error.detail ||
          "Une erreur est survenue, veuillez réessayer plus tard",
        "ERROR",
        { autoClose: true },
      );
      return;
    }
    sendToast("Informations mises à jour", "SUCCESS", { autoClose: true });
    mutate((event) => {
      return { ...event, ...res.data };
    });
  };

  const isDisabled = !event || !event.isEditable || event.isPast || isLoading;

  return (
    <form onSubmit={handleSubmit}>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Visioconférence</StyledTitle>

      <span style={{ color: style.black700 }}>
        Pour vos réunions en ligne, utilisez le service d’Action Populaire.
        Votre salon de visioconférence est déjà prêt si vous voulez
        l’utiliser&nbsp;!
      </span>

      <Spacer size="1rem" />
      <OnlineUrlField
        label="URL de votre visio-conférence sur Action Populaire"
        placeholder="URL de la visio-conférence"
        name="onlineUrl"
        value={onlineUrl}
        onChange={updateValue}
        error={errors && errors.onlineUrl}
        disabled={isDisabled}
      />

      <Spacer size="1rem" />
      <Button color="secondary" wrap disabled={isDisabled} type="submit">
        Enregistrer
      </Button>
    </form>
  );
};
EventVisio.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  eventPk: PropTypes.string,
};
export default EventVisio;
