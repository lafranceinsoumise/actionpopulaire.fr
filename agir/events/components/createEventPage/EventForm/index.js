import React, { useCallback, useMemo, useState } from "react";
import styled from "styled-components";

// import style from "@agir/front/genericComponents/_variables.scss";

import { validateData } from "./eventForm.config";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

import NameField from "./NameField";
import OrganizerGroupField from "./OrganizerGroupField";
import DateField from "./DateField";
import SubtypeField from "./SubtypeField";
import LocationField from "./LocationField";
import ContactField from "./ContactField";

const StyledForm = styled.form`
  padding-bottom: 3rem;

  fieldset {
    margin: 0;
    padding: 0;

    legend {
      font-size: 0.813rem;
      line-height: 1.5;
      font-weight: 400;
      margin: 0;
      padding-bottom: 0.75rem;

      strong {
        display: block;
        font-size: 1.125rem;
        line-height: 1.6;
        font-weight: 500;
      }
    }
  }

  & > ${Button} {
    display: block;
    margin: 0;
    width: 100%;
    justify-content: center;
  }

  & > ${Button} + p {
    padding: 1rem 0;
    font-size: 0.813rem;
    text-align: center;
  }
`;
import { DEFAULT_FORM_DATA } from "./eventForm.config";

import TEST_SUBTYPES from "./eventSubtypes.json";
const TEST_GROUPS = [
  {
    id: "abx123",
    value: "abx123",
    label: "Equipe de soutien « Nous Sommes Pour » à Angers",
  },
  { id: null, value: null, label: "À titre individuel" },
];

const EventForm = () => {
  const [formData, setFormData] = useState(DEFAULT_FORM_DATA);
  const [errors, setErrors] = useState({});

  const updateValue = useCallback((name, value) => {
    setErrors((state) => ({
      ...state,
      [name]: undefined,
    }));
    setFormData((state) => ({
      ...state,
      [name]: value,
    }));
  }, []);

  const updateDate = useCallback((startTime, endTime) => {
    setErrors((state) => ({
      ...state,
      [name]: undefined,
    }));
    setFormData((state) => ({
      ...state,
      startTime,
      endTime,
    }));
  }, []);

  const handleSubmit = useCallback(
    (e) => {
      setErrors({});
      e.preventDefault();
      console.dir(formData);
      const errors = validateData(formData);
      if (errors) {
        setErrors(errors);
      }
    },
    [formData]
  );

  const isLoading = false;
  const groups = TEST_GROUPS;
  const subtypes = TEST_SUBTYPES;

  const maySubmit = useMemo(
    () => !isLoading && Object.values(errors).filter(Boolean).length === 0,
    [errors, isLoading]
  );

  return (
    <StyledForm onSubmit={handleSubmit}>
      <NameField
        name="name"
        value={formData.name}
        onChange={updateValue}
        error={errors && errors.name}
        disabled={isLoading}
        required={false}
      />
      <Spacer size="1rem" />
      <OrganizerGroupField
        name="organizerGroup"
        value={formData.organizerGroup}
        onChange={updateValue}
        error={errors && errors.organizerGroup}
        disabled={isLoading}
        groups={groups}
        required={false}
      />
      <Spacer size="1rem" />
      <DateField
        startTime={formData.startTime}
        endTime={formData.endTime}
        error={errors && (errors.startTime || errors.endTime)}
        onChange={updateDate}
        disabled={isLoading}
        required={false}
      />
      <Spacer size="1rem" />
      <SubtypeField
        name="subtype"
        value={formData.subtype}
        subtypes={subtypes}
        onChange={updateValue}
        error={errors && errors.subtype}
        disabled={isLoading}
        required={false}
      />
      <Spacer size="1.5rem" />
      <fieldset>
        <legend>
          <strong>Lieu de l'événement</strong>
          Même si il se déroule en ligne, indiquez un lieu pour suggérer
          l’événement aux membres à proximité.
          <br />
          Indiquez votre mairie ou un café proche de chez vous pour ne pas
          rendre publique votre adresse personnelle.
        </legend>
        <LocationField
          name="location"
          location={formData.location}
          onChange={updateValue}
          error={errors && errors.location}
          disabled={isLoading}
          required={false}
        />
      </fieldset>
      <Spacer size="1.5rem" />
      <fieldset>
        <legend>
          <strong>Contact</strong>
          Affiché publiquement. N’indiquez pas votre nom complet si vous ne
          souhaitez pas apparaître dans les résultats des moteurs de recherche.
        </legend>
        <ContactField
          name="contact"
          contact={formData.contact}
          onChange={updateValue}
          error={errors && errors.contact}
          disabled={isLoading}
          required={false}
        />
      </fieldset>
      <Spacer size="2rem" />
      <Button
        disabled={isLoading || !maySubmit}
        type="submit"
        color="secondary"
        block
      >
        Créer l'événement
      </Button>
      <p>
        Vous pourrez modifier ces informations après la création de l’événement.
      </p>
    </StyledForm>
  );
};

export default EventForm;
