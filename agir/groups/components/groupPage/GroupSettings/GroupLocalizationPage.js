import React, { useState } from "react";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import TextField from "@agir/front/formComponents/TextField";
import Map from "@agir/carte/common/Map";
import HeaderPanel from "./HeaderPanel";
import BackButton from "@agir/front/genericComponents/ObjectManagement/BackButton.js";

import { StyledTitle } from "./styledComponents.js";
import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";

const StyledMap = styled(Map)`
  height: 208px;
`;

const StyledMapConfig = styled(Map)`
  height: calc(100vh - 230px);

  @media (min-width: ${style.collapse}px) {
    height: 400px;
  }
`;

const GroupLocalizationPage = (props) => {
  const { onBack, illustration } = props;
  const [formLocation, setFormLocation] = useState({});
  const [config, setConfig] = useState(null);

  const handleInputChange = (e) => {
    setFormLocation({ ...formLocation, [e.target.name]: e.target.value });
  };

  if (config) {
    return (
      <>
        <BackButton
          onBack={() => {
            setConfig(false);
          }}
        />
        <StyledTitle>Personnaliser la localisation</StyledTitle>

        <Spacer size="1rem" />
        <StyledMapConfig center={[-97.14704, 49.8844]} />

        <Spacer size="2rem" />
        <div style={{ display: "flex", justifyContent: "center" }}>
          <Button color="secondary">Enregistrer les informations</Button>
        </div>
      </>
    );
  }

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Localisation</StyledTitle>
      <Spacer size="1rem" />
      <StyledMap center={[-97.14704, 49.8844]} />
      <Spacer size="0.5rem" />
      <Button small onClick={() => setConfig(true)}>
        Personnaliser la localisation sur la carte
      </Button>
      <Spacer size="1rem" />

      <span>
        Si vous ne souhaitez pas rendre votre adresse personnelle publique,
        indiquez un endroit à proximité (café, mairie...)
        <Spacer size="0.5rem" />
        <strong>
          Merci d'indiquer une adresse précise avec numéro de rue, sans quoi le
          groupe n'apparaîtra pas sur la carte.
        </strong>
      </span>

      <Spacer size="1rem" />

      <TextField
        id="nameLocation"
        name="nameLocation"
        label="Nom du groupe*"
        onChange={handleInputChange}
        value={formLocation.nameLocation}
      />
      <Spacer size="0.5rem" />
      <TextField
        id="address"
        name="address"
        label="Adresse*"
        onChange={handleInputChange}
        value={formLocation.address}
      />
      <Spacer size="0.5rem" />
      <TextField
        id="postalCode"
        name="postalCode"
        label="Code postal*"
        onChange={handleInputChange}
        value={formLocation.postalCode}
      />
      <Spacer size="0.5rem" />
      <TextField
        id="country"
        name="country"
        label="Pays*"
        onChange={handleInputChange}
        value={formLocation.country}
      />

      <Spacer size="2rem" />
      <Button color="secondary">Enregistrer les informations</Button>

      <hr />
      <Spacer size="1rem" />
      <a href="#" style={{ color: style.redNSP }}>
        Supprimer la localisation (déconseillé)
      </a>
    </>
  );
};

export default GroupLocalizationPage;
