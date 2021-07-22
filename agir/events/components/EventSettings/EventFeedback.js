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

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents.js";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel.js";

const EventFeedback = (props) => {
  const { onBack, illustration, eventPk } = props;
  const sendToast = useToast();
  const { data: event, mutate } = useSWR(
    api.getEventEndpoint("getEvent", { eventPk })
  );

  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);
  const originalImage = useMemo(() => event?.image, [event]);
  const [imageHasChanged, setImageHasChanged] = useState(false);
  const [hasCheckedImageLicence, setHasCheckedImageLicence] = useState(false);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setErrors((errors) => ({ ...errors, [name]: null }));
    setFormData((formData) => ({ ...formData, [name]: value }));
  };

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

    console.log("formData to send", formData);

    // const res = await updateGroup(groupPk, {
    //   ...formData,
    //   image: imageHasChanged ? formData.image : undefined,
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

  useEffect(() => {
    setFormData({
      feedback: event.compteRendu,
      photo: !!event.compteRenduPhotos?.length && event.compteRenduPhotos[0],
    });
  }, [event]);

  return (
    <form onSubmit={handleSubmit}>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Compte-rendu</StyledTitle>

      <Spacer size="1rem" />

      <RichTextField
        id="feedback"
        name="feedback"
        label="Écrire un compte-rendu*"
        placeholder=""
        onChange={handleChange}
        value={formData.feedback}
        error={errors?.feedback}
      />

      <Spacer size="1rem" />

      <h4>Ajouter une image</h4>
      <ImageField
        name="image"
        value={formData.photo}
        onChange={handleChangeImage}
        error={errors?.photo}
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

      <Spacer size="2rem" />
      <Button
        color="secondary"
        $wrap
        disabled={isLoading}
        onClick={handleSubmit}
      >
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
