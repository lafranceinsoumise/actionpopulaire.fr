import PropTypes from "prop-types";
import React, { useState, useEffect } from "react";

import BackButton from "@agir/front/genericComponents/ObjectManagement/BackButton";
import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import { StyledTitle } from "@agir/groups/groupPage/GroupSettings/styledComponents.js";
import TextField from "@agir/front/formComponents/TextField";

const GroupLinkForm = (props) => {
  const { onBack, onSubmit, selectedLink, errors, isLoading } = props;
  const [linkData, setLinkData] = useState({});

  useEffect(() => {
    setLinkData(selectedLink || {});
  }, [selectedLink]);

  if (!selectedLink) {
    return null;
  }

  const isNew = !selectedLink.id;

  const handleChange = (e) => {
    setLinkData({
      ...linkData,
      [e.target.name]: e.target.value,
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(linkData);
  };

  return (
    <>
      <BackButton disabled={isLoading} onClick={onBack} />
      <StyledTitle>
        {isNew ? "Nouveau lien personnalisé" : "Modifier le lien"}
      </StyledTitle>
      <Spacer size="1rem" />
      <div>
        Attention : ces liens seront disponibles <strong>publiquement</strong>{" "}
        et tout le monde pourra y accéder. Ne partagez pas de boucles privées.
      </div>
      <Spacer size="1.5rem" />
      <form onSubmit={handleSubmit}>
        <TextField
          id="label"
          name="label"
          label="Titre à afficher"
          helpText="Exemple : « Vidéo de présentation »"
          onChange={handleChange}
          value={linkData.label || ""}
          error={errors?.label}
          required
        />
        <Spacer size="1rem" />
        <TextField
          id="url"
          name="url"
          label="URL"
          onChange={handleChange}
          value={linkData.url || ""}
          error={errors?.url}
          required
        />
        <Spacer size="1rem" />
        <Button
          type="submit"
          disabled={isLoading || !linkData.label || !linkData.url}
          color="secondary"
        >
          {isNew ? "Ajouter ce lien" : "Enregistrer"}
        </Button>
      </form>
    </>
  );
};
GroupLinkForm.propTypes = {
  onBack: PropTypes.func.isRequired,
  onSubmit: PropTypes.func.isRequired,
  selectedLink: PropTypes.shape({
    id: PropTypes.number,
    label: PropTypes.string,
    url: PropTypes.string,
  }),
  errors: PropTypes.shape({
    label: PropTypes.string,
    url: PropTypes.string,
  }),
  isLoading: PropTypes.bool,
};
export default GroupLinkForm;
