import PropTypes from "prop-types";
import React, { useState, useMemo, useEffect, useCallback } from "react";
import useSWR from "swr";

import { useToast } from "@agir/front/globalContext/hooks.js";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import RichTextField from "@agir/front/formComponents/RichText/RichTextField.js";
import ImageField from "@agir/front/formComponents/ImageField";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel";
import { updateGroup, getGroupEndpoint } from "@agir/groups/utils/api";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";

const GroupGeneralPage = (props) => {
  const { onBack, illustration, groupPk } = props;
  const sendToast = useToast();

  const { data: group, mutate } = useSWR(
    getGroupEndpoint("getGroup", { groupPk }),
  );

  const [imageHasChanged, setImageHasChanged] = useState(false);
  const [hasCheckedImageLicence, setHasCheckedImageLicence] = useState(false);
  const [formData, setFormData] = useState({});
  const [errors, setErrors] = useState({});
  const [isLoading, setIsLoading] = useState(false);

  const originalImage = useMemo(() => group?.image, [group]);

  const handleChange = useCallback((e) => {
    const { name, value } = e.target;
    setErrors((errors) => ({ ...errors, [name]: null }));
    setFormData((formData) => ({ ...formData, [name]: value }));
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

  const handleDescriptionChange = useCallback((value) => {
    // lose focus if uncomment :
    // setErrors((errors) => ({ ...errors, ["description"]: null }));
    setFormData((formData) => ({ ...formData, ["description"]: value }));
  }, []);

  const handleCheckImageLicence = useCallback((event) => {
    setHasCheckedImageLicence(event.target.checked);
    setErrors((errors) => ({ ...errors, image: null }));
  }, []);

  const handleSubmit = useCallback(
    async (e) => {
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

      const res = await updateGroup(groupPk, {
        ...formData,
        image: imageHasChanged ? formData.image : undefined,
      });

      setIsLoading(false);

      if (res.error) {
        setErrors(res.error);
        return;
      }
      sendToast("Informations mises à jour", "SUCCESS", { autoClose: true });
      mutate((group) => {
        return { ...group, ...res.data };
      });
    },
    [
      mutate,
      formData,
      groupPk,
      hasCheckedImageLicence,
      imageHasChanged,
      sendToast,
    ],
  );

  useEffect(() => {
    setFormData({
      name: group?.name,
      description: group?.description,
      image: group?.image,
    });
    setImageHasChanged(false);
    setHasCheckedImageLicence(false);
  }, [group]);

  return (
    <form onSubmit={handleSubmit}>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Général</StyledTitle>

      <Spacer size="1rem" />

      <TextField
        id="name"
        name="name"
        label="Nom du groupe*"
        onChange={handleChange}
        value={formData.name}
        error={errors?.name}
      />

      <Spacer size="1rem" />

      <RichTextField
        id="description"
        name="description"
        label="Description du groupe*"
        placeholder=""
        onChange={handleDescriptionChange}
        value={formData.description}
        error={errors?.description}
      />

      <h4>Image de la bannière</h4>
      <span style={{ color: style.black700 }}>
        Elle apparaîtra sur la page sur les réseaux sociaux.
        <br />
        Utilisez une image à peu près deux fois plus large que haute. Elle doit
        faire au minimum 1200px de large et 630px de haut pour une qualité
        optimale.
      </span>

      <Spacer size="1.5rem" />
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

      <Spacer size="2rem" />
      <Button type="submit" color="secondary" wrap disabled={isLoading}>
        Enregistrer
      </Button>
    </form>
  );
};
GroupGeneralPage.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  groupPk: PropTypes.string,
};
export default GroupGeneralPage;
