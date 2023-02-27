import PropTypes from "prop-types";
import React, { Fragment } from "react";
import useSWRImmutable from "swr/immutable";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import Spacer from "@agir/front/genericComponents/Spacer";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel";
import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";

import { getEventEndpoint } from "@agir/events/common/api";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

const EventAssets = (props) => {
  const { onBack, illustration, eventPk } = props;

  const { data: eventAssets, isLoading } = useSWRImmutable(
    getEventEndpoint("getEventAssets", { eventPk })
  );

  return (
    <div>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Ressources et documents</StyledTitle>
      <Spacer size="1rem" />
      <span style={{ color: style.black700 }}>
        Retrouvez ici la liste des ressources qui pourront vous être utiles pour
        l'organisation de votre événement.
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
        <Button link small route="helpEvents" color="secondary">
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
      <StyledTitle>Documents et visuels</StyledTitle>
      <Spacer size=".5rem" />
      <PageFadeIn
        ready={!isLoading}
        wait={
          <Skeleton style={{ height: "160px", margin: "0 0 1rem" }} boxes={3} />
        }
      >
        {Array.isArray(eventAssets) &&
          eventAssets.map((eventAsset) => (
            <Fragment key={eventAsset.id}>
              <Card>
                <p>
                  <strong>{eventAsset.name}</strong>
                </p>
                <Button
                  link
                  small
                  href={eventAsset.file}
                  color="primary"
                  icon="download"
                >
                  Télécharger le document
                </Button>
              </Card>
              <Spacer size="1rem" />
            </Fragment>
          ))}
        <Card>
          <p>
            <strong>Attestation d'assurance de la France insoumise</strong>
            <br />
            Document utile en cas de réservation d'une salle pour les événements
            publics
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
      </PageFadeIn>
      <Spacer size="2rem" />
    </div>
  );
};
EventAssets.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  eventPk: PropTypes.string,
};
export default EventAssets;
