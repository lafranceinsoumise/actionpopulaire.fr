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
  const { report, endTime, rsvped, routes, isOrganizer } = props;

  const isPast = endTime < DateTime.local();
  const canAddPictures = isPast && (rsvped || isOrganizer);

  const photos = Array.isArray(report?.photos) ? report.photos : [];
  const picture = report?.picture || null;
  const hasPictures = !!picture || photos.length > 0;

  if (!hasPictures && !canAddPictures) {
    return null;
  }

  return (
    <StyledCard>
      <h5>Photos</h5>
      <Spacer size="0.5rem" />

      {hasPictures ? (
        <Thumbnails>
          {picture && (
            <a
              key={picture}
              href={picture}
              rel="noopener noreferrer"
              target="_blank"
            >
              <img
                src={picture}
                width="400"
                height="250"
                alt="Photo de l'événement postée par l'utilisateur"
                title="Photo de l'événement postée par l'utilisateur"
              />
            </a>
          )}
          {photos.map((photo) => (
            <a
              key={photo.image}
              href={photo.image}
              rel="noopener noreferrer"
              target="_blank"
            >
              <img
                src={photo.thumbnail}
                width="400"
                height="250"
                alt={
                  photo?.legend ||
                  "Photo de l'événement postée par l'utilisateur"
                }
                title={
                  photo?.legend ||
                  "Photo de l'événement postée par l'utilisateur"
                }
              />
            </a>
          ))}
        </Thumbnails>
      ) : (
        <p>Il n'y a pas encore de photo de cet événement.</p>
      )}
      {canAddPictures && (
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
  report: PropTypes.shape({
    picture: PropTypes.object,
    photos: PropTypes.arrayOf(PropTypes.object),
  }),
  endTime: PropTypes.object,
  rsvped: PropTypes.bool,
  routes: PropTypes.object,
  isOrganizer: PropTypes.bool,
};
export default EventPhotosCard;
