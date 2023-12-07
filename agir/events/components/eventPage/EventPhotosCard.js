import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";
import { DateTime } from "luxon";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

import StyledCard from "./StyledCard";

const Thumbnails = styled.div`
  display: grid;
  grid-gap: 0.5rem;
  grid-template-columns: repeat(auto-fill, 160px);
  grid-auto-rows: 160px;
  align-items: center;
  justify-items: center;

  a {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    overflow: hidden;
  }

  img {
    margin: 0;
    width: auto;
    height: 100%;
    transform: scale(1);
    transition: transform 100ms ease-in-out;

    &:hover,
    &:focus {
      transform: scale(1.01);
      transform-origin: center center;
    }
  }
`;

const EventPhotosCard = (props) => {
  const {
    compteRenduMainPhoto,
    compteRenduPhotos,
    endTime,
    rsvped,
    routes,
    isOrganizer,
  } = props;

  const isPast = endTime < DateTime.local();
  const canAddPhotos = isPast && (rsvped || isOrganizer);
  const mainPhoto = compteRenduMainPhoto ? [compteRenduMainPhoto] : [];
  const morePhotos = compteRenduPhotos?.length ? compteRenduPhotos : [];
  const photos = mainPhoto.concat(morePhotos);

  if (photos.length === 0 && !canAddPhotos) {
    return null;
  }

  return (
    <StyledCard>
      <h5>Photos</h5>
      <Spacer size="0.5rem" />

      {photos.length > 0 ? (
        <Thumbnails>
          {photos.map((url) => {
            const legend =
              url?.legend || "Photo de l'événement postée par l'utilisateur";
            return (
              <a
                key={url.image}
                href={url.image}
                rel="noopener noreferrer"
                target="_blank"
              >
                <img
                  src={url.thumbnail}
                  width="400"
                  height="250"
                  alt={legend}
                  title={legend}
                />
              </a>
            );
          })}
        </Thumbnails>
      ) : (
        <p>Il n'y a pas encore de photo de cet événement.</p>
      )}
      {canAddPhotos && (
        <div style={{ paddingTop: "1rem" }}>
          <Button link href={routes.addPhoto}>
            Ajouter une photo
          </Button>
        </div>
      )}
    </StyledCard>
  );
};
EventPhotosCard.propTypes = {
  compteRenduMainPhoto: PropTypes.object,
  compteRenduPhotos: PropTypes.arrayOf(PropTypes.object),
  endTime: PropTypes.object,
  rsvped: PropTypes.bool,
  routes: PropTypes.object,
  isOrganizer: PropTypes.bool,
};
export default EventPhotosCard;
