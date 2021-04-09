import React, { useState } from "react";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import TextField from "@agir/front/formComponents/TextField";
import Map from "@agir/carte/common/Map";

import { StyledTitle } from "./styledComponents.js";

const GroupLocalizationPage = () => {
  const [formLocation, setFormLocation] = useState({});

  const handleInputChange = (e) => {
    //setFormLocation({...formLocation, `${e.target.name}`: e.target.value })
    const newFormLocation = { ...formLocation };
    newFormLocation[e.target.name] = e.target.value;
    setFormLocation(newFormLocation);
  };

  return (
    <>
      <StyledTitle>Localisation</StyledTitle>

      <Spacer size="1rem" />

      <Map center={[-97.14704, 49.8844]} style={{ height: "260px" }} />

      <Spacer size="0.5rem" />

      <Button small>Personnaliser la localisation sur la carte</Button>

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
    </>
  );
};

export default GroupLocalizationPage;
