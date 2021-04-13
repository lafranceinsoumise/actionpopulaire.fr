import React from "react";

import Button from "@agir/front/genericComponents/Button";
import ShareLink from "@agir/front/genericComponents/ShareLink.js";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import HeaderPanel from "./HeaderPanel";

import { StyledTitle } from "./styledComponents.js";

const GroupFinancePage = (props) => {
  const { onBack, illustration } = props;

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Solliciter des dons pour mon groupe</StyledTitle>

      <span>
        Pour solliciter des dons pour votre groupe, vous pouvez utiliser le lien
        ci-dessous.
      </span>

      <ShareLink
        label="Copier"
        url="https://actionpopulaire.fr/dons/?group=627ff9f0-e53d-478d-91fb-1a22c76a34d0"
      />

      <Spacer size="1rem" />

      <StyledTitle>Dons alloués aux personnes de mon groupe</StyledTitle>

      <span>
        Personne n'a encore alloué de dons à vos actions. Vous pouvez le faire
        sur la page de dons.
        <br />
        Vous pouvez déjà créer une demande, mais vous ne pourrez la faire
        valider que lorsque votre allocation sera suffisante.
      </span>

      <Spacer size="2rem" />
      <Button color="secondary">Je crée une demande de dépense</Button>
    </>
  );
};

export default GroupFinancePage;
