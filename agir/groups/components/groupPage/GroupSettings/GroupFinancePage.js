import React from "react";

import Button from "@agir/front/genericComponents/Button";
import ShareLink from "@agir/front/genericComponents/ShareLink.js";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import HeaderPanel from "./HeaderPanel";

import { StyledTitle } from "./styledComponents.js";

const GroupFinancePage = (props) => {
  const { onBack, illustration } = props;

  const PRICE = 30;

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />

      <StyledTitle>Dons alloués aux personnes de mon groupe</StyledTitle>

      <Spacer size="1rem" />

      <span style={{ fontSize: "2rem" }}>{PRICE} €</span>

      <Spacer size="1rem" />

      <div>
        {!PRICE && (
          <>
            Personne n'a encore alloué de dons à vos actions.
            <br />
          </>
        )}
        Vous pouvez allouer des dons à vos actions sur la{" "}
        <a href="">page de dons</a>.
        <Spacer size="0.5rem" />
        Vous pouvez déjà créer une demande, mais vous ne pourrez la faire
        valider que lorsque votre allocation sera suffisante.
      </div>

      <Spacer size="1rem" />

      <Button>Allouer un don</Button>
      <Button>Je crée une demande de dépense</Button>

      <Spacer size="1rem" />

      <StyledTitle>Solliciter des dons pour mon groupe</StyledTitle>

      <span>Partagez ce lien pour solliciter des dons pour votre groupe :</span>

      <ShareLink
        color="primary"
        label="Copier le lien"
        url="https://actionpopulaire.fr/dons/?group=627ff9f0-e53d-478d-91fb-1a22c76a34d0"
      />
    </>
  );
};

export default GroupFinancePage;
