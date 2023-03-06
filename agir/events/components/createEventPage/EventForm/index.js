import React, { useCallback, useEffect, useState } from "react";
import { useHistory, useLocation } from "react-router-dom";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { createEvent } from "@agir/events/common/api";
import {
  DEFAULT_FORM_DATA,
  validateData,
} from "@agir/events/common/eventForm.config";
import { useEventFormOptions } from "@agir/events/common/hooks";
import { routeConfig } from "@agir/front/app/routes.config";

import UnloadPrompt from "@agir/front/app/UnloadPrompt";
import LocationField from "@agir/front/formComponents/LocationField";
import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

import OrganizerGroupField from "@agir/events/common/OrganizerGroupField";
import { scrollToError } from "@agir/front/app/utils";
import ContactField from "./ContactField";
import DateField from "./DateField";
import DescriptionField from "./DescriptionField";
import EventImageField from "./EventImageField";
import NameField from "./NameField";
import OnlineUrlField from "./OnlineUrlField";
import SubtypeField from "./SubtypeField";

const StyledGlobalError = styled.p`
  padding: 0 0 1rem;
  margin: 0;
  font-size: 1rem;
  text-align: center;
  color: ${style.redNSP};
`;
const StyledForm = styled.form`
  padding-bottom: 3rem;

  fieldset {
    margin: 0;
    padding: 0;

    legend {
      font-size: 1rem;
      line-height: 1.5;
      font-weight: 400;
      margin: 0;
      padding-bottom: 1.5rem;

      strong {
        display: block;
        font-size: 1.5rem;
        line-height: 1.6;
        font-weight: 500;
      }

      em {
        text-decoration: underline;
        font-style: normal;
      }
    }
  }
`;

const formatErrors = (errors, fields = DEFAULT_FORM_DATA) => {
  if (typeof errors !== "object") {
    return errors;
  }
  return Object.entries(errors).reduce(
    (errors, [field, error]) => ({
      ...errors,
      [typeof fields[field] !== "undefined" ? field : "global"]: Array.isArray(
        error
      )
        ? error[0]
        : formatErrors(error, fields[field]),
    }),
    {}
  );
};

const EventForm = () => {
  const [formData, setFormData] = useState(DEFAULT_FORM_DATA);
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const [newEventPk, setNewEventPk] = useState(null);

  const history = useHistory();
  const { search } = useLocation();
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

  const updateNestedValue = useCallback((parentName, name, value) => {
    setErrors((state) => {
      if (!state[parentName] || !state[parentName][name]) {
        return state;
      }
      const newState = { ...state };
      if (Object.keys(newState[parentName]).length > 1) {
        newState[parentName] = { ...newState[parentName] };
        delete newState[parentName][name];
      } else {
        newState[parentName] = undefined;
      }
      return newState;
    });
    setFormData((state) => ({
      ...state,
      [parentName]: {
        ...(state[parentName] || {}),
        [name]: value,
        isDefault: false,
      },
    }));
  }, []);

  const updateDate = useCallback((startTime, endTime) => {
    setErrors((state) => ({
      ...state,
      startTime: undefined,
      endTime: undefined,
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
      setErrors((state) => ({
        ...state,
        contact: undefined,
      }));
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
      setErrors((state) => ({
        ...state,
        location: undefined,
      }));
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
      let errors = validateData(formData);
      if (formData.image && !formData.image.hasLicense) {
        errors = errors || {};
        errors.image =
          "Vous devez acceptez la licence pour envoyer votre image en conformité";
      }
      if (errors) {
        setErrors(errors);
        scrollToError(errors, window, 100);
        return;
      }
      setIsLoading(true);
      const result = await createEvent(formData);
      setIsLoading(false);
      if (result.errors) {
        const errors = formatErrors(result.errors);
        setErrors(errors);
        scrollToError(errors, window, 100);
        return;
      }
      if (!result.data || !result.data.id) {
        setErrors({ global: "Une erreur est survenue" });
        return;
      }
      setNewEventPk(result.data.id);
    },
    [formData]
  );

  useEffect(() => {
    if (newEventPk) {
      const route = routeConfig.eventDetails.getLink({ eventPk: newEventPk });
      history.push(route);
    }
  }, [history, newEventPk]);

  useEffect(() => {
    if (!search) {
      return;
    }
    const params = new URLSearchParams(search);
    if (
      !formData.organizerGroup &&
      params.get("group") &&
      options.organizerGroup
    ) {
      const organizerGroup = options.organizerGroup.find(
        (g) => g.id === params.get("group")
      );
      organizerGroup &&
        setFormData((state) => ({
          ...state,
          organizerGroup,
        }));
    }
    if (!formData.subtype && params.get("subtype") && options.subtype) {
      const subtype = options.subtype.find(
        (g) => g.label === params.get("subtype")
      );
      subtype &&
        setFormData((state) => ({
          ...state,
          subtype,
        }));
    }
  }, [search, options, formData]);

  useEffect(() => {
    if (
      options &&
      options.organizerGroup &&
      options.organizerGroup.length === 1 &&
      !formData.organizerGroup
    ) {
      setFormData((state) => ({
        ...state,
        organizerGroup: options.organizerGroup[0],
      }));
    }
  }, [options, formData]);

  return (
    <StyledForm onSubmit={handleSubmit} disabled={isLoading} noValidate>
      <Spacer size="0" data-scroll="subtype" />
      <SubtypeField
        name="subtype"
        value={formData.subtype}
        options={options.subtype}
        onChange={updateValue}
        error={errors && errors.subtype}
        disabled={isLoading}
        required
      />
      <Spacer size="1rem" data-scroll="name" />
      <NameField
        name="name"
        value={formData.name}
        defaultValue={formData?.subtype?.description || ""}
        onChange={updateValue}
        error={errors && errors.name}
        disabled={isLoading}
        required
      />
      <Spacer size="1rem" data-scroll="organizerGroup" />
      <OrganizerGroupField
        name="organizerGroup"
        value={formData.organizerGroup}
        onChange={updateValue}
        error={errors && errors.organizerGroup}
        disabled={isLoading}
        required
        options={options.organizerGroup}
      />
      <div data-scroll="endTime" />
      <div data-scroll="timezone" />
      <Spacer size="1rem" data-scroll="startTime" />
      <DateField
        startTime={formData.startTime}
        endTime={formData.endTime}
        timezone={formData.timezone}
        error={
          errors && (errors.startTime || errors.endTime || errors.timezone)
        }
        onChange={updateDate}
        onChangeTimezone={(timezone) => updateValue("timezone", timezone)}
        disabled={isLoading}
        required
      />
      <Spacer size="1.25rem" data-scroll="description" />
      <DescriptionField
        name="description"
        value={formData.description}
        onChange={updateValue}
        error={errors && errors.description}
        disabled={isLoading}
      />
      <Spacer size="1.25rem" data-scroll="image" />
      <EventImageField
        name="image"
        value={formData.image}
        onChange={updateValue}
        error={errors?.image}
        disabled={isLoading}
      />
      <Spacer size="2rem" />
      <fieldset>
        <legend style={{ paddingBottom: "0" }}>
          <strong>Lieu de l'événement</strong>
          <em>Même s'il se déroule en ligne</em>, indiquez un lieu pour suggérer
          l’événement aux personnes à proximité, une mairie ou un café pour ne
          pas rendre votre adresse publique.
        </legend>
        <Spacer size="1.5rem" data-scroll="onlineUrl" />
        <OnlineUrlField
          label="Visio-conférence"
          name="onlineUrl"
          onChange={updateValue}
          error={errors && errors.onlineUrl}
          value={formData.onlineUrl}
          placeholder="URL de la visio-conférence (facultatif)"
        />
        <Spacer size="1.5rem" data-scroll="location" />
        <LocationField
          name="location"
          location={formData.location}
          onChange={updateNestedValue}
          error={errors && errors.location}
          help={{
            name: "Si l'événement se déroule en ligne, vous pouvez le préciser ici",
          }}
          disabled={isLoading}
          required
        />
      </fieldset>
      <Spacer size="1.5rem" data-scroll="contact" />
      <fieldset>
        <legend>
          <strong>Contact</strong>
          Affiché publiquement. N’indiquez pas votre nom complet si vous ne
          souhaitez pas apparaître dans les résultats des moteurs de recherche.
        </legend>
        <ContactField
          name="contact"
          contact={formData.contact}
          onChange={updateNestedValue}
          error={errors && errors.contact}
          disabled={isLoading}
          required
        />
      </fieldset>
      <Spacer size="1rem" data-scroll="global" />
      {errors && errors.global && (
        <StyledGlobalError>{errors.global}</StyledGlobalError>
      )}
      <Button
        loading={isLoading}
        disabled={isLoading}
        type="submit"
        color="secondary"
        block
      >
        Créer l'événement
      </Button>
      <p
        style={{ padding: "1rem 0", fontSize: "0.813rem", textAlign: "center" }}
      >
        Vous pourrez modifier ces informations après la création de l’événement.
      </p>
      <UnloadPrompt enabled={!newEventPk} allowedRoutes="createEvent" />
    </StyledForm>
  );
};
export default EventForm;
