import PropTypes from "prop-types";
import React, { useState, useMemo, useEffect, useCallback } from "react";
import styled from "styled-components";
import useSWR from "swr";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import RichTextField from "@agir/front/formComponents/RichText/RichTextField";
import ImageField from "@agir/front/formComponents/ImageField";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import Spacer from "@agir/front/genericComponents/Spacer";
import DateField from "@agir/events/createEventPage/EventForm/DateField";
import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel";
import OrganizerGroupField from "@agir/events/common/OrganizerGroupField";
import EventSubtypeField from "@agir/events/EventSettings/EventSubtypeField";

import { DEFAULT_FORM_DATA } from "@agir/events/common/eventForm.config";
import * as api from "@agir/events/common/api";
import { useToast } from "@agir/front/globalContext/hooks";
import { useEventFormOptions } from "@agir/events/common/hooks";

const StyledDateField = styled(DateField)`
  @media (min-width: ${style.collapse}px) {
    && {
      grid-template-columns: 190px 159px 180px;
    }
  }
`;

const EventGeneral = (props) => {
  const { onBack, illustration, eventPk } = props;
  const sendToast = useToast();
  const options = useEventFormOptions();
  const { data: event, mutate } = useSWR(
    api.getEventEndpoint("getEvent", { eventPk })
  );

  const [formData, setFormData] = useState({
    name: DEFAULT_FORM_DATA.name,
    organizerGroup: DEFAULT_FORM_DATA.organizerGroup,
    startTime: DEFAULT_FORM_DATA.startTime,
    endTime: DEFAULT_FORM_DATA.endTime,
    timezone: DEFAULT_FORM_DATA.timezone,
    description: DEFAULT_FORM_DATA.description,
    facebook: DEFAULT_FORM_DATA.facebook,
    image: DEFAULT_FORM_DATA.image,
    subtype: DEFAULT_FORM_DATA.subtype,
  });

  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const originalImage = useMemo(() => event?.image, [event]);
  const [imageHasChanged, setImageHasChanged] = useState(false);
  const [hasCheckedImageLicence, setHasCheckedImageLicence] = useState(false);

  useEffect(() => {
    setImageHasChanged(false);
    setHasCheckedImageLicence(false);

    setFormData((state) => ({
      ...state,
      name: event.name,
      description: event.description,
      facebook: event.routes.facebook,
      image: event.illustration?.banner,
      subtype: event.subtype,
      startTime: event.startTime,
      endTime: event.endTime,
      timezone: event.timezone,
    }));
  }, [event]);

  useEffect(() => {
    if (
      formData.organizerGroup !== null ||
      !event ||
      !options?.organizerGroup
    ) {
      return;
    }

    if (event?.groups[0]) {
      setFormData((state) => ({
        ...state,
        organizerGroup: options.organizerGroup.find(
          ({ id }) => id === event.groups[0].id
        ) || {
          ...event.groups[0],
          label: event.groups[0],
        },
      }));
      return;
    }

    setFormData((state) => ({
      ...state,
      organizerGroup: options.organizerGroup.find(({ id }) => id === null),
    }));
  }, [formData.organizerGroup, event, options]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setErrors((errors) => ({ ...errors, [name]: null }));
    setFormData((formData) => ({ ...formData, [name]: value }));
  };

  const handleChangeValue = useCallback((name, value) => {
    setErrors((errors) => ({ ...errors, [name]: null }));
    setFormData((formData) => ({ ...formData, [name]: value }));
  }, []);

  const handleDescriptionChange = useCallback((value) => {
    setFormData((formData) => ({ ...formData, description: value }));
  }, []);

  const handleChangeImage = useCallback(
    (value) => {
      setErrors((errors) => ({ ...errors, image: null }));
      setImageHasChanged(value !== originalImage);
      value && value !== originalImage && setHasCheckedImageLicence(false);
      setFormData((formData) => ({ ...formData, image: value }));
    },
    [originalImage]
  );

  const handleCheckImageLicence = useCallback((event) => {
    setHasCheckedImageLicence(event.target.checked);
    setErrors((errors) => ({ ...errors, image: null }));
  }, []);

  const updateDate = useCallback(
    (startTime, endTime) => {
      handleChangeValue("startTime", startTime);
      handleChangeValue("endTime", endTime);
    },
    [handleChangeValue]
  );

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setIsLoading(true);

    if (formData.image && imageHasChanged && !hasCheckedImageLicence) {
      setErrors((errors) => ({
        ...errors,
        image:
          "Vous devez acceptez les licences pour envoyer votre image en conformité.",
      }));
      setIsLoading(false);
      return;
    }

    const res = await api.updateEvent(eventPk, {
      ...formData,
      image: imageHasChanged ? formData.image : undefined,
      organizerGroup: formData?.organizerGroup?.id,
    });

    setIsLoading(false);

    if (res.error) {
      setErrors(res.error);
      sendToast(
        "Une erreur est survenue, veuillez réessayer plus tard",
        "ERROR",
        { autoClose: true }
      );
      return;
    }
    sendToast("Informations mises à jour", "SUCCESS", { autoClose: true });
    mutate((event) => ({ ...event, ...res.data }));
  };

  const isDisabled = !event || event.isPast || isLoading;

  return (
    <>
      <form onSubmit={handleSubmit}>
        <HeaderPanel onBack={onBack} illustration={illustration} />
        <StyledTitle>Général</StyledTitle>
        <span style={{ color: style.black700 }}>
          Ces informations seront affichées en public.
        </span>
        <Spacer size="1rem" />
        <TextField
          id="name"
          name="name"
          label="Nom de l'événement*"
          onChange={handleChange}
          value={formData.name}
          error={errors?.name}
          disabled={isDisabled}
        />
        <Spacer size="1rem" />
        <OrganizerGroupField
          name="organizerGroup"
          value={formData.organizerGroup}
          onChange={handleChangeValue}
          error={errors?.organizerGroup}
          disabled={isDisabled}
          options={options.organizerGroup}
          required
        />
        <Spacer size="1rem" />
        <div>
          <StyledDateField
            startTime={formData.startTime}
            endTime={formData.endTime}
            timezone={formData.timezone}
            showTimezone
            error={
              errors && (errors.startTime || errors.endTime || errors.timezone)
            }
            onChange={updateDate}
            onChangeTimezone={(e) => handleChangeValue("timezone", e)}
            disabled={isDisabled}
            required
          />
        </div>
        <Spacer size="1rem" />
        <RichTextField
          id="description"
          name="description"
          label="Description*"
          placeholder=""
          onChange={handleDescriptionChange}
          value={formData.description}
          error={errors?.description}
          disabled={isDisabled}
        />
        <Spacer size="1rem" />
        <TextField
          id="facebook"
          name="facebook"
          label="Url de l'événement sur Facebook"
          onChange={handleChange}
          value={formData.facebook}
          error={errors?.facebook}
          disabled={isDisabled}
        />
        <h4>Image mise en avant</h4>
        <span style={{ color: style.black700 }}>
          Taille : 1200*630px ou plus. Elle apparaîtra sur la page et sur les
          réseaux sociaux.
        </span>
        <Spacer size="0.5rem" />
        <ImageField
          name="image"
          value={formData.image}
          onChange={handleChangeImage}
          error={errors?.image}
          accept=".jpg,.jpeg,.gif,.png"
          disabled={isDisabled}
        />
        {formData.image && imageHasChanged && (
          <>
            <Spacer size="0.5rem" />
            <CheckboxField
              value={hasCheckedImageLicence}
              label={
                <span style={{ color: style.black700 }}>
                  En important une image, je certifie être le propriétaire des
                  droits et accepte de la partager sous licence libre{" "}
                  <a href="https://creativecommons.org/licenses/by-nc-sa/3.0/fr/">
                    Creative Commons CC-BY-NC 3.0
                  </a>
                  .
                </span>
              }
              onChange={handleCheckImageLicence}
              disabled={isDisabled}
            />
          </>
        )}
        <Spacer size="1rem" />
        <EventSubtypeField
          name="subtype"
          value={formData.subtype}
          options={options?.subtype}
          onChange={handleChangeValue}
          disabled={isDisabled}
        />

        <Spacer size="2rem" />
        <Button color="secondary" wrap disabled={isDisabled} type="submit">
          Enregistrer
        </Button>
      </form>
    </>
  );
};

EventGeneral.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  eventPk: PropTypes.string,
};
export default EventGeneral;
