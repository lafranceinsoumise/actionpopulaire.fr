import PropTypes from "prop-types";
import React, { useState, useEffect, useCallback } from "react";
import useSWR, { mutate } from "swr";

import { useToast } from "@agir/front/globalContext/hooks.js";
import * as api from "@agir/events/common/api";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import Spacer from "@agir/front/genericComponents/Spacer.js";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents.js";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel.js";

const EventContact = (props) => {
  const { onBack, illustration, eventPk } = props;

  const { data: event, mutate: mutateAPI } = useSWR(
    api.getEventEndpoint("getDetailAdvanced", { eventPk }),
  );
  const sendToast = useToast();

  const [contact, setContact] = useState({
    name: "",
    email: "",
    phone: "",
    hidePhone: false,
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    setContact({
      name: event?.contact.name,
      email: event?.contact.email,
      phone: event?.contact.phone,
      hidePhone: event?.contact.hidePhone,
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
    [contact],
  );

  const handleSubmit = async (e) => {
    e.preventDefault();

    setErrors({});
    setIsLoading(true);
    const res = await api.updateEvent(eventPk, { contact });
    setIsLoading(false);

    if (res.error) {
      setErrors(res.error?.contact);
      return;
    }
    sendToast("Informations mises à jour", "SUCCESS", { autoClose: true });
    mutateAPI((event) => {
      return { ...event, ...res.data };
    });
    mutate(api.getEventEndpoint("getEvent", { eventPk }));
  };

  const isDisabled = !event || !event.isEditable || isLoading;

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
        disabled={isDisabled}
        required
      />
      <Spacer size="1rem" />

      <TextField
        id="email"
        name="email"
        type="email"
        label="Adresse e-mail à contacter*"
        onChange={handleChange}
        value={contact.email}
        error={errors?.email}
        disabled={isDisabled}
        required
      />
      <Spacer size="1rem" />

      <TextField
        id="phone"
        name="phone"
        label="Numéro de téléphone à contacter*"
        onChange={handleChange}
        value={contact.phone}
        error={errors?.phone}
        disabled={isDisabled}
        required
      />
      <Spacer size="1rem" />

      <CheckboxField
        name="hidePhone"
        label="Cacher le numéro de téléphone"
        value={contact?.hidePhone}
        error={errors?.hidePhone}
        onChange={handleCheckboxChange}
        disabled={isDisabled}
      />

      <Spacer size="2rem" />
      <Button color="secondary" wrap disabled={isDisabled} type="submit">
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
