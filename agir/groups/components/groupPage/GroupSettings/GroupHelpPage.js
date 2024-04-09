import PropTypes from "prop-types";
import React from "react";

import * as style from "@agir/front/genericComponents/_variables.scss";

import FileCard from "@agir/front/genericComponents/FileCard";
import HelpCenterCard from "@agir/front/genericComponents/HelpCenterCard";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel";
import Spacer from "@agir/front/genericComponents/Spacer";
import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";

import { useGroup } from "@agir/groups/groupPage/hooks/group.js";

const GroupHelpPage = (props) => {
  const { groupPk, onBack, illustration } = props;
  const group = useGroup(groupPk);

  return (
    <div>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Ressources</StyledTitle>
      <Spacer size="1rem" />
      <span style={{ color: style.black700 }}>
        Retrouvez ici la liste des ressources qui pourront vous être utiles pour
        l'animation et la gestion de votre groupe.
      </span>
      <Spacer size="1rem" />
      <StyledTitle>Centre d'aide</StyledTitle>
      <Spacer size=".5rem" />
      <HelpCenterCard type="group" />
      <Spacer size="1rem" />
      <StyledTitle>Documents</StyledTitle>
      <Spacer size=".5rem" />
      {group?.routes?.downloadAttendanceList && (
        <>
          <FileCard
            title="Liste d'émargement"
            text="Une liste d'émargement des membres à utiliser lors des événements internes du groupe pour noter les personnes présentes"
            icon="file-text"
            href={group.routes.downloadAttendanceList}
            downloadLabel="Télécharger la liste d'émargement"
            isNew
          />
          <Spacer size="1rem" />
        </>
      )}
      <FileCard
        title="Attestation d'assurance de la France insoumise"
        text="Document utile en cas de réservation d'une salle pour les événements publics"
        icon="file-text"
        route="attestationAssurance"
        downloadLabel="Télécharger l'attestation"
      />
      <Spacer size="1rem" />
      <FileCard
        title="Charte des groupes d'action"
        text="La charte que tous les animateurs et toutes les animatrices de groupe s’engagent à respecter."
        icon="file-text"
        route="charteEquipes"
        downloadLabel="Voir la charte"
        downloadIcon="eye"
      />
      <Spacer size="1rem" />
      <FileCard
        title="Livret de l’animateur·rice"
        text="Un guide pratique qui répond à la plupart des intérrogations concernant l'animation d'un groupe d'action."
        icon="file-text"
        route="livretAnimateurice"
        downloadLabel="Télécharger le livret"
      />
      <Spacer size="2rem" />
    </div>
  );
};
GroupHelpPage.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  groupPk: PropTypes.string,
};
export default GroupHelpPage;
