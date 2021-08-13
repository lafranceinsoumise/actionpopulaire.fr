import PropTypes from "prop-types";
import React, { useState, useEffect, useCallback } from "react";
import styled from "styled-components";
import useSWR from "swr";

import { useToast } from "@agir/front/globalContext/hooks.js";
import * as api from "@agir/events/common/api";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import Map from "@agir/carte/common/Map";
import BackButton from "@agir/front/genericComponents/ObjectManagement/BackButton.js";
import LocationField from "@agir/front/formComponents/LocationField.js";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents.js";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel.js";

const StyledMap = styled(Map)`
  height: 208px;
`;

const StyledMapConfig = styled(Map)`
  height: calc(100vh - 230px);

  @media (min-width: ${style.collapse}px) {
    height: 400px;
  }
`;

const EventLocation = (props) => {
  const { onBack, illustration, eventPk } = props;

  let { data: event, mutate } = useSWR(
    api.getEventEndpoint("getEvent", { eventPk })
  );
  const updateLocationUrl = api.getEventEndpoint("updateLocation", { eventPk });
  const sendToast = useToast();

  const [formLocation, setFormLocation] = useState({});
  const [config, setConfig] = useState(null);
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(true);

  const handleInputChange = useCallback((_, name, value) => {
    setFormLocation((formLocation) => ({ ...formLocation, [name]: value }));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setErrors({});
    setIsLoading(true);
    const res = await api.updateEvent(eventPk, { location: formLocation });
    setIsLoading(false);
    if (res.error) {
      setErrors(res.error);
      return;
    }
    sendToast("Informations mises à jour", "SUCCESS", { autoClose: true });
    mutate((event) => {
      return { ...event, ...res.data };
    });
  };

  useEffect(() => {
    setIsLoading(false);
    setFormLocation({
      name: event?.location.name,
      address1: event?.location.address1,
      address2: event?.location.address2,
      zip: event?.location.zip,
      city: event?.location.city,
      country: event?.location.country,
    });
  }, [event]);

  if (config) {
    return (
      <>
        <BackButton
          onClick={() => {
            setConfig(false);
          }}
        />
        <StyledTitle>Personnaliser la localisation</StyledTitle>

        <Spacer size="1rem" />
        <StyledMapConfig center={event?.location?.coordinates?.coordinates} />

        <Spacer size="2rem" />
        <div style={{ display: "flex", justifyContent: "center" }}>
          <Button color="secondary" $wrap disabled={isLoading}>
            Enregistrer les informations
          </Button>
        </div>
      </>
    );
  }

  return (
    <form onSubmit={handleSubmit}>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Localisation</StyledTitle>
      <Spacer size="1rem" />
      <StyledMap
        center={event?.location?.coordinates?.coordinates || []}
        iconConfiguration={event?.iconConfiguration}
      />
      <Spacer size="0.5rem" />
      {/* <Button small $wrap onClick={() => setConfig(true)}>
        Personnaliser la localisation sur la carte
      </Button> */}
      <Button as="a" small $wrap href={updateLocationUrl}>
        Personnaliser la localisation sur la carte
      </Button>
      <Spacer size="1rem" />

      <span style={{ color: style.black700 }}>
        Si vous ne souhaitez pas rendre cette adresse publique, indiquez un
        endroit à proximité (café, mairie...)
        <Spacer size="0.5rem" />
        <strong>
          Merci d'indiquer une adresse précise avec numéro de rue, sans quoi
          l'événement n'apparaîtra pas sur la carte.
        </strong>
      </span>

      <Spacer size="1.5rem" />
      <LocationField
        name="location"
        location={formLocation}
        onChange={handleInputChange}
        error={errors && errors.location}
        required
      />

      <Spacer size="2rem" />
      <Button color="secondary" $wrap disabled={isLoading}>
        Enregistrer
      </Button>

      {/* <hr />
      <Spacer size="1rem" />
      <a href="#" style={{ color: style.redNSP }}>
        Supprimer la localisation (déconseillé)
      </a> */}
    </form>
  );
};
EventLocation.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  eventPk: PropTypes.string,
};
export default EventLocation;
