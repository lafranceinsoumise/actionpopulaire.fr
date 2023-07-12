import PropTypes from "prop-types";
import React, { Fragment } from "react";
import useSWRImmutable from "swr/immutable";

import style from "@agir/front/genericComponents/_variables.scss";

import FileCard from "@agir/front/genericComponents/FileCard";
import HelpCenterCard from "@agir/front/genericComponents/HelpCenterCard";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel";
import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";

import { getEventEndpoint } from "@agir/events/common/api";

const EventAssets = (props) => {
  const { onBack, illustration, eventPk } = props;

  const { data: eventAssets, isLoading } = useSWRImmutable(
    getEventEndpoint("getEventAssets", { eventPk }),
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
      <HelpCenterCard type="event" />
      <Spacer size="1rem" />
      <StyledTitle>Documents</StyledTitle>
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
              <FileCard
                title={eventAsset.name}
                text={`Format ${eventAsset.format} - ${eventAsset.size}`}
                icon="image"
                route={eventAsset.file}
                downloadLabel="Télécharger le visuel"
              />
              <Spacer size="1rem" />
            </Fragment>
          ))}
        <FileCard
          title="Attestation d'assurance de la France insoumise"
          text="Document utile en cas de réservation d'une salle pour les événements publics"
          icon="file-text"
          route="attestationAssurance"
          downloadLabel="Télécharger l'attestation"
        />
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
