import PropTypes from "prop-types";
import React, { useState, useEffect, useCallback } from "react";
import useSWR from "swr";

import { useToast } from "@agir/front/globalContext/hooks.js";
import * as api from "@agir/events/common/api";

import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import DateField from "@agir/events/createEventPage/EventForm/DateField";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents.js";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel.js";

const StyledDateField = styled(DateField)`
  @media (min-width: ${style.collapse}px) {
    && {
      grid-template-columns: 190px 170px 160px;
    }
  }
`;

const EventContact = (props) => {
  const { onBack, illustration, eventPk } = props;

  const { data: event, mutate } = useSWR(
    api.getEventEndpoint("getEvent", { eventPk })
  );
  console.log("event swr", event);
  const sendToast = useToast();

  const [contact, setContact] = useState({});
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [imageHasChanged, setImageHasChanged] = useState(false);
  const [hasCheckedImageLicence, setHasCheckedImageLicence] = useState(false);

  useEffect(() => {
    setContact({
      name: event.contact.name,
      email: event.contact.email,
      phone: event.contact.phone,
      hidePhone: event.contact.hidePhone,
    });
  }, [event]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setErrors((errors) => ({ ...errors, [name]: null }));
    setContact((contact) => ({ ...contact, [name]: value }));
  };

  const handleCheckboxChange = useCallback(
    (e) => {
      setContact({ ...contact, [e.target.name]: e.target.checked });
    },
    [contact]
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setIsLoading(true);

    if (contact.image && imageHasChanged && !hasCheckedImageLicence) {
      setErrors((errors) => ({
        ...errors,
        image:
          "Vous devez acceptez les licences pour envoyer votre image en conformité.",
      }));
      setIsLoading(false);
      return;
    }

    console.log("contact to send", contact);

    // const res = await updateGroup(groupPk, {
    //   ...contact,
    //   image: imageHasChanged ? contact.image : undefined,
    // });

    setIsLoading(false);

    // if (res.error) {
    //   setErrors(res.error);
    //   return;
    // }
    // sendToast("Informations mises à jour", "SUCCESS", { autoClose: true });
    // mutate((group) => {
    //   return { ...group, ...res.data };
    // });
  };

  return (
    <form onSubmit={handleSubmit}>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Moyens de contact</StyledTitle>

      <span style={{ color: style.black700 }}>
        Ces informations seront affichées en public. Conseillé : créez une
        adresse e-mail pour votre groupe et n’utilisez pas une adresse
        personnelle.
      </span>

      <Spacer size="1rem" />

      <TextField
        id="name"
        name="name"
        label="Nom de la/les personnes à contacter*"
        onChange={handleChange}
        value={contact.name}
        error={errors?.name}
      />
      <Spacer size="1rem" />

      <TextField
        id="email"
        name="email"
        label="Adresse e-mail à contacter*"
        onChange={handleChange}
        value={contact.email}
        error={errors?.email}
      />
      <Spacer size="1rem" />

      <TextField
        id="phone"
        name="phone"
        label="Numéro de téléphone à contacter*"
        onChange={handleChange}
        value={contact.phone}
        error={errors?.phone}
      />
      <Spacer size="1rem" />

      <CheckboxField
        name="hidePhone"
        label="Cacher le numéro de téléphone"
        value={contact?.hidePhone}
        error={errors?.hidePhone}
        onChange={handleCheckboxChange}
      />

      <Spacer size="2rem" />
      <Button
        color="secondary"
        $wrap
        disabled={isLoading}
        onClick={handleSubmit}
      >
        Enregistrer
      </Button>
    </form>
  );
};
EventContact.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  eventPk: PropTypes.string,
};
export default EventContact;
