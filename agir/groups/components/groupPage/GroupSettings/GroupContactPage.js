import React, { useState } from "react";

import Spacer from "@agir/front/genericComponents/Spacer.js";
import Button from "@agir/front/genericComponents/Button";
import TextField from "@agir/front/formComponents/TextField";
import CheckboxField from "@agir/front/formComponents/CheckboxField";
import HeaderPanel from "./HeaderPanel";

import { StyledTitle } from "./styledComponents.js";

const GroupContactPage = (props) => {
  const { onBack, illustration } = props;
  const [formData, setFormData] = useState({});

  const handleCheckboxChange = (e) => {
    const newFormData = { ...formData };
    newFormData[e.target.name] = !formData[e.target.name];
    setFormData(newFormData);
  };

  const handleChange = (e) => {
    const newFormData = { ...formData };
    newFormData[e.target.name] = e.target.value;
    setFormData(newFormData);
  };

  return (
    <>
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
        label="Nom de la / les personnes à contacter*"
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
      <Button color="secondary">Enregistrer</Button>
    </>
  );
};

export default GroupContactPage;
