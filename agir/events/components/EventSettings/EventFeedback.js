import PropTypes from "prop-types";
import React, { useState, useMemo, useCallback, useEffect } from "react";
import useSWR from "swr";

import { useToast } from "@agir/front/globalContext/hooks.js";
import * as api from "@agir/events/common/api";

import style from "@agir/front/genericComponents/_variables.scss";

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
    api.getEventEndpoint("getEvent", { eventPk })
  );

  const [formData, setFormData] = useState({
    compteRendu: "",
    compteRenduPhotos: "",
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
      setFormData((formData) => ({ ...formData, compteRenduPhotos: value }));
    },
    [originalImage]
  );

  const handleCheckImageLicence = useCallback((event) => {
    setHasCheckedImageLicence(event.target.checked);
    setErrors((errors) => ({ ...errors, image: null }));
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();

    setErrors({});
    setIsLoading(true);

    if (
      formData.compteRenduPhotos &&
      imageHasChanged &&
      !hasCheckedImageLicence
    ) {
      setErrors((errors) => ({
        ...errors,
        image:
          "Vous devez acceptez les licences pour envoyer votre image en conformité.",
      }));
      setIsLoading(false);
      return;
    }

    if (!imageHasChanged) delete formData.compteRenduPhotos;

    const res = await api.updateEvent(eventPk, {
      compteRendu: formData.compteRendu,
      compteRenduPhotos: formData.compteRenduPhotos,
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
    setFormData({
      compteRendu: event.compteRendu,
      compteRenduPhotos:
        event.compteRenduPhotos?.length &&
        event.compteRenduPhotos[0]?.isReportImage
          ? event.compteRenduPhotos[0]?.image
          : null,
    });
  }, [event]);

  return (
    <form onSubmit={handleSubmit}>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Compte-rendu</StyledTitle>

      <Spacer size="1rem" />
      <RichTextField
        id="feedback"
        name="compteRendu"
        label="Écrire un compte-rendu*"
        placeholder=""
        onChange={(e) => handleChange("compteRendu", e)}
        value={formData.compteRendu}
        error={errors?.compteRendu}
      />

      <Spacer size="1rem" />

      <h4>
        {!formData.compteRenduPhotos || imageHasChanged
          ? "Ajouter une photo"
          : "Photo"}
      </h4>
      <span style={{ color: style.black700 }}>
        Cette image apparaîtra en tête de votre compte-rendu, et dans les
        partages que vous ferez du compte-rendu sur les réseaux sociaux.
      </span>
      <Spacer size="0.5rem" />
      <ImageField
        name="compteRenduPhotos"
        value={formData.compteRenduPhotos}
        onChange={handleChangeImage}
        error={errors?.image}
        accept=".jpg,.jpeg,.gif,.png"
      />

      {formData.compteRenduPhotos && imageHasChanged && (
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

      {formData.compteRenduPhotos && (
        <>
          <Spacer size="0.5rem" />
          <Button link small href={event?.routes.addPhoto}>
            Ajouter d'autres photos
          </Button>
        </>
      )}

      <Spacer size="2rem" />
      <Button color="secondary" wrap disabled={isLoading} type="submit">
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
