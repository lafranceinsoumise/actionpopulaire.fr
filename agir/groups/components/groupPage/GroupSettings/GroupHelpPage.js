import PropTypes from "prop-types";
import React from "react";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import Spacer from "@agir/front/genericComponents/Spacer";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";

const GroupHelpPage = (props) => {
  const { onBack, illustration } = props;

  return (
    <div>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Ressources et liens utiles</StyledTitle>
      <Spacer size="1rem" />
      <span style={{ color: style.black700 }}>
        Retrouvez ici la liste des ressources qui pourront vous être utiles pour
        l'animation et la gestion de votre groupe.
      </span>
      <Spacer size="1rem" />
      <StyledTitle>Centre d'aide</StyledTitle>
      <Spacer size=".5rem" />
      <Card>
        <p>
          Un centre d'aide est à votre disposition avec des fiches pratiques et
          les réponses aux questions le plus fréquemment posées.
        </p>
        <p>
          Un page de contact est également disponible pour des questions plus
          spécifiques.
        </p>
        <Spacer size="0.5rem" />
        <Button link small route="helpGroups" color="secondary">
          Acceder au centre d'aide
        </Button>
        <Spacer size="0.5rem" />
        <Button link small route="helpIndex" color="secondary">
          Voir les fiches pratiques
        </Button>
        <Spacer size="0.5rem" />
        <Button link small route="contact" color="default">
          Nous contacter
        </Button>
      </Card>
      <Spacer size="1rem" />
      <StyledTitle>Documents</StyledTitle>
      <Spacer size=".5rem" />
      <Card>
        <p>
          <strong>Attestation d'assurance de la France insoumise</strong>
          <br />
          Document utile en cas de réservation d'une salle pour les événements
          publics de votre groupe
        </p>
        <Button
          link
          small
          route="attestationAssurance"
          color="primary"
          icon="download"
        >
          Télécharger l'attestation
        </Button>
      </Card>
      <Spacer size="1rem" />
      <Card>
        <p>
          <strong>Charte des groupes d'action</strong>
          <br />
          La charte que tous les animateurs et toutes les animatrices de groupe
          s’engagent à respecter.
        </p>
        <Button link small route="charteEquipes" color="primary" icon="eye">
          Voir la charte
        </Button>
      </Card>
      <Spacer size="1rem" />
      <Card>
        <p>
          <strong>Livret de l’animateur·rice</strong>
          <br />
          Un guide pratique qui répond à la plupart des intérrogations concernat
          l'animation d'un groupe d'action
        </p>
        <Button
          link
          small
          route="livretAnimateurice"
          color="primary"
          icon="download"
        >
          Télécharger le livret
        </Button>
      </Card>
      <Spacer size="2rem" />
    </div>
  );
};
GroupHelpPage.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
};
export default GroupHelpPage;
