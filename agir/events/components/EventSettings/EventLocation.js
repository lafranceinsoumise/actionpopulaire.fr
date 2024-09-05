import PropTypes from "prop-types";
import React, { useState, useEffect, useCallback } from "react";
import styled from "styled-components";
import useSWR from "swr";

import { useToast } from "@agir/front/globalContext/hooks";
import * as api from "@agir/events/common/api";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";
import Map from "@agir/carte/common/Map";
import LocationField from "@agir/front/formComponents/LocationField";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel";

const StyledMap = styled(Map)`
  && {
    width: 100%;
    height: 208px;
  }
`;

const EventLocation = (props) => {
  const { onBack, illustration, eventPk } = props;

  let { data: event, mutate } = useSWR(
    api.getEventEndpoint("getEvent", { eventPk }),
  );
  const updateLocationUrl = api.getEventEndpoint("updateLocation", { eventPk });
  const sendToast = useToast();

  const [formLocation, setFormLocation] = useState({
    name: "",
    address1: "",
    address2: "",
    zip: "",
    city: "",
    country: "FR",
  });

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
    mutate((event) => ({
      ...event,
      location: { ...res.data.location, coordinates: null },
    }));
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

  const isDisabled = !event || !event.isEditable || event.isPast || isLoading;

  return (
    <form onSubmit={handleSubmit}>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Localisation</StyledTitle>
      <Spacer size="1rem" />
      <StyledMap
        center={event?.location?.coordinates?.coordinates || []}
        iconConfiguration={
          typeof event?.subtype === "object" ? event.subtype : undefined
        }
      />
      <Spacer size="0.5rem" />
      <Button link small wrap href={updateLocationUrl} disabled={isDisabled}>
        Personnaliser la localisation sur la carte
      </Button>
      <Spacer size="1rem" />

      <span
        css={`
          color: ${(props) => props.theme.text700};
        `}
      >
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
        disabled={isDisabled}
      />
      <Spacer size="1rem" />
      {errors.global && (
        <p
          css={`
            color: ${(props) => props.theme.error500};
            margin: 0;
          `}
        >
          ⚠&ensp;{errors.global}
        </p>
      )}
      <Spacer size="1rem" />
      <Button type="submit" color="secondary" $wrap disabled={isDisabled}>
        Enregistrer
      </Button>
    </form>
  );
};
EventLocation.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  eventPk: PropTypes.string,
};
export default EventLocation;
