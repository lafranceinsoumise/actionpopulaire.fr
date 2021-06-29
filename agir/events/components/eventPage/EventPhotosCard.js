import React from "react";
import styled from "styled-components";
import Button from "../../../front/components/genericComponents/Button";
import { DateTime } from "luxon";
import Card from "../../../front/components/genericComponents/Card";

const Thumbnails = styled.div`
  display: grid;
  grid-gap: 0.5rem;
  grid-template-columns: repeat(auto-fill, 160px);
  grid-auto-rows: 160px;
  align-items: center;
  justify-items: center;

  a {
    display: block;
    width: 100%;
    height: 100%;
    overflow: hidden;
  }

  img {
    margin: 0;
    width: 100%;
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

const StyledButton = styled(Button)`
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  border-radius: ${style.borderRadius};
  margin-top: 16px;
`;

const StyledCard = styled(Card)`
  p {
    margin: 0;
  }
`;

const EventPhotosCard = ({ compteRenduPhotos, endTime, rsvp, routes }) => {
  const isPast = endTime < DateTime.local();

  return (
    <>
      {isPast ? (
        compteRenduPhotos.length > 0 || rsvp === "CO" ? (
          <StyledCard>
            <b>Photos</b>
            {compteRenduPhotos.length > 0 ? (
              <Thumbnails>
                {compteRenduPhotos.map((url) => (
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
                      alt={
                        url.legend ||
                        "Photo de l'événement postée par l'utilisateur"
                      }
                      title={
                        url.legend ||
                        "Photo de l'événement postée par l'utilisateur"
                      }
                    />
                  </a>
                ))}
              </Thumbnails>
            ) : (
              <p>Il n'y a pas encore de photo de cet événement.</p>
            )}
            {rsvp === "CO" && (
              <div>
                <StyledButton as="a" href={routes.addPhoto}>
                  Ajouter une photo
                </StyledButton>
              </div>
            )}
          </StyledCard>
        ) : null
      ) : null}
    </>
  );
};

export default EventPhotosCard;
