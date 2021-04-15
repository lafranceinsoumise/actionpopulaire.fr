import React, { useState, useCallback } from "react";

import Spacer from "@agir/front/genericComponents/Spacer.js";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import HeaderPanel from "./HeaderPanel";

import { StyledTitle } from "./styledComponents.js";

const GroupContactPage = (props) => {
  const { onBack, illustration } = props;
  const [formData, setFormData] = useState({});

  const handleCheckboxChange = useCallback(
    (e) => {
      setFormData({ ...formData, [e.target.name]: e.target.checked });
    },
    [formData]
  );

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

  return (
    <form onSubmit={handleSubmit}>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Moyens de contact</StyledTitle>

      <Spacer size="1rem" />

      <span>Ces informations seront affichées en public.</span>
      <Spacer size="0.5rem" />
      <span>
        Conseillé : créez une adresse e-mail pour votre groupe et n’utilisez pas
        une adresse personnelle.
      </span>

      <Spacer size="2rem" />

      <TextField
        id="name"
        name="name"
        label="Nom de la / des personnes à contacter*"
        onChange={handleChange}
        value={formData.name}
      />

      <Spacer size="1rem" />

      <TextField
        id="email"
        name="email"
        label="Adresse e-mail du groupe*"
        onChange={handleChange}
        value={formData.email}
      />

      <Spacer size="1rem" />

      <TextField
        id="phone"
        name="phone"
        label="Numéro de téléphone à contacter*"
        onChange={handleChange}
        value={formData.phone}
      />

      <Spacer size="0.5rem" />

      <CheckboxField
        name="hidePhone"
        label="Cacher le numéro de téléphone"
        value={formData.hidePhone}
        onChange={handleCheckboxChange}
      />

      <Spacer size="2rem" />
      <Button color="secondary" type="submit">
        Enregistrer
      </Button>
    </form>
  );
};

export default GroupContactPage;
