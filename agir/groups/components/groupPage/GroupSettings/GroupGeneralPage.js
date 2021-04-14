import React, { useState, useCallback } from "react";

import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import HeaderPanel from "./HeaderPanel";

import { StyledTitle } from "./styledComponents.js";

const GroupGeneralPage = (props) => {
  const { onBack, illustration } = props;
  const [name, setName] = useState("Nom du groupe");
  const [description, setDescription] = useState("Description");

  const handleNameChange = useCallback((e) => {
    setName(e.target.value);
  }, []);

  const handleDescriptionChange = useCallback((e) => {
    setDescription(e.target.value);
  }, []);

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Général</StyledTitle>

      <Spacer size="1rem" />

      <TextField
        id="name"
        name="name"
        label="Nom du groupe*"
        onChange={handleNameChange}
        value={name}
      />

      <Spacer size="1rem" />

      <TextField
        textArea={true}
        id="description"
        name="description"
        label="Description du groupe*"
        placeholder=""
        onChange={handleDescriptionChange}
        value={description}
      />

      <h4>Image de la bannière</h4>
      <span>
        Elle apparaîtra sur la page sur les réseaux sociaux.
        <br />
        Utilisez une image à peu près deux fois plus large que haute. Elle doit
        faire au minimum 1200px de large et 630px de haut pour une qualité
        optimale.
      </span>

      <Spacer size="1rem" />
      <Button small>Ajouter une image</Button>

      <Spacer size="2rem" />
      <Button color="secondary">Enregistrer les informations</Button>
    </>
  );
};

export default GroupGeneralPage;
