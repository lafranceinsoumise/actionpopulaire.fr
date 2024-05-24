import PropTypes from "prop-types";
import React, { useState, useMemo, useCallback, useEffect } from "react";
import useSWR from "swr";

import { useToast } from "@agir/front/globalContext/hooks.js";
import * as api from "@agir/events/common/api";

import * as style from "@agir/front/genericComponents/_variables.scss";

import ImageField from "@agir/front/formComponents/ImageField";
import Button from "@agir/front/genericComponents/Button";
import RichTextField from "@agir/front/formComponents/RichText/RichTextField.js";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import CheckboxField from "@agir/front/formComponents/CheckboxField";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents.js";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel.js";

const EventFeedback = (props) => {
  const { eventPk, onBack, illustration } = props;
  const sendToast = useToast();
  const { data: event, mutate } = useSWR(
    api.getEventEndpoint("getEvent", { eventPk }),
  );
  const [formData, setFormData] = useState({
    content: "",
    picture: "",
  });
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const originalImage = useMemo(() => event?.image, [event]);
  const [imageHasChanged, setImageHasChanged] = useState(false);
  const [hasCheckedImageLicence, setHasCheckedImageLicence] = useState(false);

  const handleChange = (name, value) => {
    // setErrors((errors) => ({ ...errors, [name]: null }));
    setFormData((formData) => ({ ...formData, [name]: value }));
  };

  const handleChangeImage = useCallback(
    (value) => {
      setErrors((errors) => ({ ...errors, image: null }));
      setImageHasChanged(value !== originalImage);
      value && value !== originalImage && setHasCheckedImageLicence(false);
      setFormData((formData) => ({ ...formData, picture: value }));
    },
    [originalImage],
  );

  const handleCheckImageLicence = useCallback((event) => {
    setHasCheckedImageLicence(event.target.checked);
    setErrors((errors) => ({ ...errors, image: null }));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setErrors({});
    setIsLoading(true);

    if (formData.picture && imageHasChanged && !hasCheckedImageLicence) {
      setErrors((errors) => ({
        ...errors,
        image:
          "Vous devez acceptez les licences pour envoyer votre image en conformité.",
      }));
      setIsLoading(false);
      return;
    }

    const res = await api.updateEvent(eventPk, {
      report: {
        content: formData.content,
        picture: imageHasChanged ? formData.picture : undefined,
      },
    });
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
    setImageHasChanged(false);
    setFormData((state) => event?.report || state);
  }, [event]);

  const isDisabled = !event || !event.isEditable || isLoading;

  return (
    <form onSubmit={handleSubmit}>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Compte rendu</StyledTitle>
      <p style={{ color: style.black700 }}>
        Le compte rendu et les photos de l'événement seront visibles uniquement
        pour les organisateur·ices, les participant·es ainsi que pour les
        membres actifs des groupes organisateurs.
      </p>

      <Spacer size="1rem" />
      <RichTextField
        id="feedback"
        name="content"
        label="Écrire un compte rendu*"
        placeholder=""
        onChange={(e) => handleChange("content", e)}
        value={formData.content}
        error={errors?.report?.content}
        disabled={isDisabled}
      />

      <Spacer size="1rem" />

      <h4>Photo de l'événement</h4>
      <Spacer size="0.5rem" />
      <ImageField
        name="picture"
        value={formData.picture}
        onChange={handleChangeImage}
        error={errors?.image || errors?.report?.picture}
        accept=".jpg,.jpeg,.png"
        disabled={isDisabled}
      />

      {formData.picture && imageHasChanged && (
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

      {formData.picture && !imageHasChanged && (
        <>
          <Spacer size="0.5rem" />
          <Button link small href={event?.routes.addPhoto}>
            Ajouter d'autres photos
          </Button>
        </>
      )}

      <Spacer size="2rem" />
      <Button color="secondary" wrap disabled={isDisabled} type="submit">
        Enregistrer les informations
      </Button>
    </form>
  );
};
EventFeedback.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  eventPk: PropTypes.string,
};
export default EventFeedback;
