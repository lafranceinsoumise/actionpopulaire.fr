import React, { useState, useEffect, useCallback } from "react";

import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import ImageField from "@agir/front/formComponents/ImageField";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import HeaderPanel from "./HeaderPanel";
import { useGroup } from "@agir/groups/groupPage/hooks/group.js";

import { StyledTitle } from "./styledComponents.js";

const GroupGeneralPage = (props) => {
  const { onBack, illustration, groupPk } = props;

  const group = useGroup(groupPk);
  console.log("usegroup : ", group);
  const [formData, setFormData] = useState({});

  const handleChange = useCallback(
    (e) => {
      setFormData({ ...formData, [e.target.name]: e.target.value });
    },
    [formData]
  );

  const handleSubmit = useCallback(
    (e) => {
      e.preventDefault();
      console.log("SUBMIT", formData);
    },
    [formData]
  );

  useEffect(() => {
    setFormData({ name: group.name, description: group.description });
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
      />

      <Spacer size="1rem" />

      <TextField
        textArea={true}
        id="description"
        name="description"
        label="Description du groupe*"
        placeholder=""
        onChange={handleChange}
        value={formData.description}
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
      <ImageField value={""} onChange={() => {}} />

      <Spacer size="2rem" />
      <Button color="secondary" wrap>
        Enregistrer les informations
      </Button>
    </form>
  );
};

export default GroupGeneralPage;
