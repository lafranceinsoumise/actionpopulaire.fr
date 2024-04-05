import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import styled from "styled-components";
import useSWR from "swr";

import * as style from "@agir/front/genericComponents/_variables.scss";

import DateField from "@agir/events/createEventPage/EventForm/DateField";
import EventSubtypeField from "@agir/events/EventSettings/EventSubtypeField";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import ImageField from "@agir/front/formComponents/ImageField";
import RichTextField from "@agir/front/formComponents/RichText/RichTextField";
import TextField from "@agir/front/formComponents/TextField";
import Button from "@agir/front/genericComponents/Button";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel";
import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";
import Spacer from "@agir/front/genericComponents/Spacer";

import * as api from "@agir/events/common/api";
import { DEFAULT_FORM_DATA } from "@agir/events/common/eventForm.config";
import { useEventFormOptions } from "@agir/events/common/hooks";
import { useToast } from "@agir/front/globalContext/hooks";

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
    api.getEventEndpoint("getEvent", { eventPk }),
  );

  const [formData, setFormData] = useState({
    name: DEFAULT_FORM_DATA.name,
    startTime: "",
    endTime: "",
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
      subtype: event.subtype.isVisible ? event.subtype : undefined,
      startTime: event.startTime,
      endTime: event.endTime,
      timezone: event.timezone,
    }));
  }, [event]);

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
    [originalImage],
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
    [handleChangeValue],
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
    });

    setIsLoading(false);

    if (res.error) {
      setErrors(res.error);
      sendToast(
        res.error.detail ||
          (Array.isArray(res.error.subtype) && res.error.subtype[0]) ||
          "Une erreur est survenue, veuillez réessayer plus tard",
        "ERROR",
        { autoClose: true },
      );
      return;
    }
    sendToast("Informations mises à jour", "SUCCESS", { autoClose: true });
    mutate((event) => ({ ...event, ...res.data }));
  };

  const isDisabled = !event || !event.isEditable || event.isPast || isLoading;

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
        {event.subtype.isVisible && (
          <>
            <Spacer size="1rem" />
            <EventSubtypeField
              name="subtype"
              value={formData.subtype}
              options={options?.subtype}
              lastUsedIds={options?.lastUsedSubtypeIds}
              onChange={handleChangeValue}
              disabled={isDisabled}
            />
          </>
        )}
        <Spacer size="1rem" />
        {errors.global && (
          <p
            css={`
              color: ${(props) => props.theme.redNSP};
              margin: 0;
            `}
          >
            ⚠&ensp;{errors.global}
          </p>
        )}
        <Spacer size="1rem" />
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
