import PropTypes from "prop-types";
import React, { Fragment } from "react";
import styled from "styled-components";
import useSWRImmutable from "swr/immutable";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel";
import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";

import { getEventEndpoint } from "@agir/events/common/api";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledCard = styled(Card)`
  display: flex;
  flex-flow: column nowrap;
  align-items: flex-start;
  gap: 0.5rem;

  & > * {
    flex: 0 0 auto;
    margin: 0;
  }

  & > h5 {
    display: flex;
    flex-flow: row nowrap;
    gap: 0.5rem;
    align-items: flex-start;
    line-height: 1.5;
    min-height: 1px;
    max-width: 100%;

    & > ${RawFeatherIcon} {
      flex: 0 0 auto;
    }

    & > span {
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
    }
  }

  & > p {
    font-size: 0.875rem;
    color: ${style.black700};
    margin-bottom: 0.25rem;
  }
`;

const EventAssets = (props) => {
  const { onBack, illustration, eventPk } = props;

  const { data: eventAssets, isLoading } = useSWRImmutable(
    getEventEndpoint("getEventAssets", { eventPk })
  );

  return (
    <div>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Ressources</StyledTitle>
      <Spacer size="1rem" />
      <span style={{ color: style.black700 }}>
        Retrouvez ici la liste des ressources qui pourront vous être utiles dans
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
      <StyledTitle>Visuels et documents</StyledTitle>
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
              <StyledCard>
                <h5>
                  <RawFeatherIcon name="image" small />
                  <span>{eventAsset.name}</span>
                </h5>
                <p>
                  Format {eventAsset.format} - {eventAsset.size}
                </p>
                <Button
                  link
                  small
                  href={eventAsset.file}
                  color="primary"
                  icon="download"
                >
                  Télécharger le visuel
                </Button>
              </StyledCard>
              <Spacer size="1rem" />
            </Fragment>
          ))}
        <StyledCard>
          <h5>
            <RawFeatherIcon name="file-text" small />
            <span>Attestation d'assurance de la France insoumise</span>
          </h5>
          <p>
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
        </StyledCard>
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
