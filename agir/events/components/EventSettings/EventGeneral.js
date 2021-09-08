import PropTypes from "prop-types";
import React, { useState, useMemo, useEffect, useCallback } from "react";
import useSWR from "swr";

import { useToast } from "@agir/front/globalContext/hooks.js";
import { useTransition } from "@react-spring/web";

import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import RichTextField from "@agir/front/formComponents/RichText/RichTextField.js";
import ImageField from "@agir/front/formComponents/ImageField";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import DateField from "@agir/events/createEventPage/EventForm/DateField";
import Link from "@agir/front/app/Link";
import BackButton from "@agir/front/genericComponents/ObjectManagement/BackButton.js";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents.js";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel.js";
import { PanelWrapper } from "@agir/front/genericComponents/ObjectManagement/PanelWrapper";

import * as api from "@agir/events/common/api";

import { useEventFormOptions } from "@agir/events/common/hooks";

import {
  DefaultOption,
  StyledDefaultOptions,
} from "@agir/events/createEventPage/EventForm/SubtypeField.js";

import { SubtypeOptions } from "@agir/events/common/SubtypePanel";

import { EVENT_TYPES } from "@agir/events/common/utils";

const slideInTransition = {
  from: { transform: "translateX(66%)" },
  enter: { transform: "translateX(0%)" },
  leave: { transform: "translateX(100%)" },
};

const StyledDateField = styled(DateField)`
  @media (min-width: ${style.collapse}px) {
    && {
      grid-template-columns: 190px 159px 180px;
    }
  }
`;

const ChooseSubtype = ({ options, selected, onClick, onBack }) => {
  return (
    <>
      <BackButton onClick={onBack} />
      <StyledTitle>Choisir le type de l'événement</StyledTitle>
      <Spacer size="1rem" />
      <SubtypeOptions options={options} onClick={onClick} selected={selected} />
    </>
  );
};

const EventGeneral = (props) => {
  const { onBack, illustration, eventPk } = props;
  const sendToast = useToast();

  const { data: event, mutate } = useSWR(
    api.getEventEndpoint("getEvent", { eventPk })
  );

  const eventOptions = useEventFormOptions();
  const subtypes = useMemo(
    () => (Array.isArray(eventOptions.subtype) ? eventOptions.subtype : []),
    [eventOptions.subtype]
  );
  const options = useMemo(() => {
    const categories = {};
    subtypes.forEach((subtype) => {
      const category =
        subtype.type && EVENT_TYPES[subtype.type] ? subtype.type : "O";
      categories[category] = categories[category] || {
        ...EVENT_TYPES[category],
      };
      categories[category].subtypes = categories[category].subtypes || [];
      categories[category].subtypes.push(subtype);
    });

    return Object.values(categories).filter((category) =>
      Array.isArray(category.subtypes)
    );
  }, [subtypes]);

  const [formData, setFormData] = useState({
    name: "",
    description: "",
    facebook: null,
    image: null,
    subtype: "",
    startTime: "",
    endTime: "",
    timezone: "",
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const originalImage = useMemo(() => event?.image, [event]);
  const [imageHasChanged, setImageHasChanged] = useState(false);
  const [hasCheckedImageLicence, setHasCheckedImageLicence] = useState(false);
  const [submenuOpen, setSubmenuOpen] = useState(false);

  useEffect(() => {
    setFormData({
      name: event.name,
      description: event.description,
      facebook: event.routes.facebook,
      image: event.illustration?.banner,
      subtype: event.subtype,
      startTime: event.startTime,
      endTime: event.endTime,
      timezone: event.timezone,
    });
  }, [event]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setErrors((errors) => ({ ...errors, [name]: null }));
    setFormData((formData) => ({ ...formData, [name]: value }));
  };

  const handleChangeValue = (name, value) => {
    setFormData((formData) => ({ ...formData, [name]: value }));
  };

  const handleDescriptionChange = useCallback((value) => {
    setFormData((formData) => ({ ...formData, ["description"]: value }));
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrors({});
    setIsLoading(true);

    if (!formData.facebook) delete formData.facebook;

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
        "Une erreur est survenue, veuillez réessayer plus tard",
        "ERROR",
        { autoClose: true }
      );
      return;
    }
    sendToast("Informations mises à jour", "SUCCESS", { autoClose: true });
    mutate((event) => {
      return { ...event, ...res.data };
    });
  };

  const transition = useTransition(submenuOpen, slideInTransition);

  const handleBack = useCallback(() => {
    setSubmenuOpen(false);
    setErrors({});
  }, []);

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
            disabled={isLoading}
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
        />

        <Spacer size="1rem" />
        <TextField
          id="facebook"
          name="facebook"
          label="Url de l'événement sur Facebook"
          onChange={handleChange}
          value={formData.facebook}
          error={errors?.facebook}
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
            />
          </>
        )}

        <Spacer size="1rem" />
        <div>
          <label>Type de l'événement</label>
        </div>

        {formData?.subtype && (
          <div>
            <StyledDefaultOptions style={{ display: "inline-flex" }}>
              <DefaultOption
                option={formData.subtype}
                onClick={() => setSubmenuOpen(true)}
                selected
              />
            </StyledDefaultOptions>
            <Link
              href={"#"}
              onClick={() => setSubmenuOpen(true)}
              style={{ marginLeft: "0.5rem" }}
            >
              Changer
            </Link>
          </div>
        )}

        <Spacer size="2rem" />
        <Button color="secondary" wrap disabled={isLoading} type="submit">
          Enregistrer
        </Button>
      </form>

      {transition(
        (style, item) =>
          item && (
            <PanelWrapper style={style}>
              <ChooseSubtype
                options={options}
                onClick={(e) => {
                  handleChangeValue("subtype", e);
                  setSubmenuOpen(false);
                }}
                onBack={handleBack}
              />
            </PanelWrapper>
          )
      )}
    </>
  );
};

EventGeneral.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  eventPk: PropTypes.string,
};
export default EventGeneral;
