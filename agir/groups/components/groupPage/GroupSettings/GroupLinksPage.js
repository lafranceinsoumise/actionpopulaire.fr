import React from "react";

import Spacer from "@agir/front/genericComponents/Spacer.js";
import GroupLink from "./GroupLink.js";
import { StyledTitle } from "./styledComponents.js";

const GroupLinksPage = () => {
  return (
    <>
      <StyledTitle>Liens et réseaux sociaux de l’équipe</StyledTitle>

      <Spacer size="1rem" />

      <GroupLink
        label="Présentation sur Youtube"
        url="https://actionpopulaire.fr"
      />
      <hr />
      <GroupLink label="Groupe Facebook" url="https://actionpopulaire.fr" />
      <hr />
      <GroupLink label="Boucle Telegram" url="https://actionpopulaire.fr" />
      <hr />

      <a href="https://actionpopulaire.fr">+ Ajouter un lien</a>
    </>
  );
};

export default GroupLinksPage;
