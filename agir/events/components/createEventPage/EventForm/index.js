import axios from "@agir/lib/utils/axios";
import qs from "querystring";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import styled from "styled-components";
import useSWR from "swr";

import { validateData } from "./eventForm.config";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

import NameField from "./NameField";
import OrganizerGroupField from "./OrganizerGroupField";
import DateField from "./DateField";
import ForUsersField from "./ForUsersField";
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

const createEvent = async (data) => {
  const result = {
    data: null,
    error: null,
  };
  const url = "/evenements/creer/form/";
  const body = qs.stringify({
    name: data.name,
    contact_email: data.contact.email,
    contact_name: data.contact.name,
    contact_phone: data.contact.phone,
    contact_hide_phone: data.contact.hidePhone,
    start_time: data.startTime,
    end_time: data.endTime,
    location_name: data.location.name,
    location_address1: data.location.address1,
    location_address2: data.location.address2,
    location_zip: data.location.zip,
    location_city: data.location.city,
    location_country: data.location.country,
    subtype: data.subtype.label,
    as_group: data.organizerGroup.id,
    for_users: data.forUsers,
    legal: JSON.stringify({}),
  });

  try {
    const response = await axios.post(url, body);
    result.data = response.data;
  } catch (e) {
    result.error = (e.response && e.response.data) || e.message;
  }

  return result;
};

const useEventFormOptions = () => {
  const { data: eventOptions } = useSWR(`/api/evenements/options/`);

  const organizerGroup = useMemo(() => {
    if (eventOptions && Array.isArray(eventOptions.organizerGroup)) {
      return [
        ...eventOptions.organizerGroup.map((group) => ({
          ...group,
          label: group.name,
          value: group.id,
        })),
        {
          id: null,
          value: null,
          label: "À titre individuel",
          contact: eventOptions.defaultContact,
        },
      ];
    }
  }, [eventOptions]);

  return eventOptions
    ? {
        ...eventOptions,
        organizerGroup,
      }
    : {};
};

const EventForm = () => {
  const [formData, setFormData] = useState(DEFAULT_FORM_DATA);
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const options = useEventFormOptions();

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

  useEffect(() => {
    if (formData.contact.isDefault && formData.organizerGroup) {
      const contact = formData.organizerGroup.contact
        ? Object.keys(DEFAULT_FORM_DATA.contact).reduce(
            (result, key) => ({
              ...result,
              [key]:
                formData.organizerGroup.contact[key] ||
                DEFAULT_FORM_DATA.contact[key],
            }),
            {}
          )
        : DEFAULT_FORM_DATA.contact;
      setFormData((state) => ({
        ...state,
        contact,
      }));
    }

    if (formData.location.isDefault && formData.organizerGroup) {
      const location = formData.organizerGroup.location
        ? Object.keys(DEFAULT_FORM_DATA.location).reduce(
            (result, key) => ({
              ...result,
              [key]:
                formData.organizerGroup.location[key] ||
                DEFAULT_FORM_DATA.location[key],
            }),
            {}
          )
        : DEFAULT_FORM_DATA.location;
      setFormData((state) => ({
        ...state,
        location,
      }));
    }
  }, [
    formData.location.isDefault,
    formData.contact.isDefault,
    formData.organizerGroup,
  ]);

  const handleSubmit = useCallback(
    async (e) => {
      e.preventDefault();
      setErrors({});
      const errors = validateData(formData);
      if (errors) {
        setErrors(errors);
        return;
      }
      setIsLoading(true);
      const result = await createEvent(formData);
      console.log(result);
      setIsLoading(false);
    },
    [formData]
  );

  const maySubmit = useMemo(
    () => !isLoading && Object.values(errors).filter(Boolean).length === 0,
    [errors, isLoading]
  );

  return (
    <StyledForm onSubmit={handleSubmit} disabled={!maySubmit}>
      <NameField
        name="name"
        value={formData.name}
        onChange={updateValue}
        error={errors && errors.name}
        disabled={isLoading}
        required
      />
      <Spacer size="1rem" />
      <OrganizerGroupField
        name="organizerGroup"
        value={formData.organizerGroup}
        onChange={updateValue}
        error={errors && errors.organizerGroup}
        disabled={isLoading}
        required
        options={options.organizerGroup}
      />
      <Spacer size="1rem" />
      <DateField
        startTime={formData.startTime}
        endTime={formData.endTime}
        error={errors && (errors.startTime || errors.endTime)}
        onChange={updateDate}
        disabled={isLoading}
        required
      />
      <Spacer size="1rem" />
      <ForUsersField
        name="forUsers"
        value={formData.forUsers}
        onChange={updateValue}
        options={options.forUsers}
        error={errors && errors.forUsers}
        disabled={isLoading}
        required
      />
      <Spacer size="1rem" />
      <SubtypeField
        name="subtype"
        value={formData.subtype}
        options={options.subtype}
        onChange={updateValue}
        error={errors && errors.subtype}
        disabled={isLoading}
        required
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
          required
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
          required
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
