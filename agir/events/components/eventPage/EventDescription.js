import React from "react";
import PropTypes from "prop-types";

import styled from "styled-components";

import { Column, Row } from "@agir/front/genericComponents/grid";
import { DateTime } from "luxon";
import Button from "@agir/front/genericComponents/Button";
import Collapsible from "@agir/front/genericComponents/Collapsible.js";

const DescriptionSection = styled.div`
  margin: 0;

  &:empty {
    margin: 0;
  }

  & + & {
    margin-top: 1rem;
  }

  & > * {
    margin-top: 0;
    margin-bottom: 1rem;

    &:empty,
    &:last-child {
      margin-bottom: 0;
    }
  }

  h2 {
    font-size: 1.25rem;
  }
`;

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

const EventDescription = ({
  compteRendu,
  compteRenduPhotos,
  illustration,
  description,
  isOrganizer,
  endTime,
  rsvp,
  routes,
}) => {
  const isPast = endTime < DateTime.local();

  return (
    <>
      {isPast ? (
        compteRenduPhotos.length > 0 || rsvp === "CO" ? (
          <DescriptionSection>
            <h2>Photos de l'événement</h2>
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
                <Button as="a" href={routes.addPhoto} color="secondary">
                  Ajouter une photo
                </Button>
              </div>
            )}
          </DescriptionSection>
        ) : null
      ) : null}

      {isPast && (compteRendu || isOrganizer) ? (
        <DescriptionSection>
          <h2>Compte-rendu</h2>
          {compteRendu ? (
            <Collapsible
              dangerouslySetInnerHTML={{ __html: compteRendu }}
              style={{ margin: "1em 0 3em" }}
              fadingOverflow
            />
          ) : (
            <p>Il n'y a pas encore de compte-rendu de cet événement.</p>
          )}
          {isOrganizer && endTime < DateTime.local() && (
            <div>
              <Button
                as="a"
                color="primary"
                href={routes.compteRendu}
                style={{ margin: "1em 1em 0 0" }}
              >
                {compteRendu ? "Modifier le" : "Ajouter un"} compte-rendu
              </Button>
            </div>
          )}
        </DescriptionSection>
      ) : null}

      {illustration && (
        <DescriptionSection>
          <img
            src={illustration}
            alt="Image d'illustration de l'événement postée par l'utilisateur"
            style={{
              maxWidth: "100%",
              height: "auto",
              maxHeight: "500px",
            }}
          />
        </DescriptionSection>
      )}

      {description ? (
        <DescriptionSection>
          <h2>L'événement</h2>
          <Collapsible
            dangerouslySetInnerHTML={{ __html: description }}
            fadingOverflow
          />
        </DescriptionSection>
      ) : null}

      {!description && isOrganizer && endTime > DateTime.local() && (
        <DescriptionSection>
          <h2>Ajoutez une description !</h2>
          <p>
            Donner tous les informations nécessaires aux participants de votre
            événement. Comment accéder au lieu, quel est le programme, les liens
            pour être tenu au courant... Et ajoutez une image !
          </p>
          <div>
            <Button as="a" color="primary" href={routes.edit}>
              Ajouter une description
            </Button>
          </div>
        </DescriptionSection>
      )}
    </>
  );
};

EventDescription.propTypes = {
  compteRendu: PropTypes.string,
  compteRenduPhotos: PropTypes.arrayOf(
    PropTypes.shape({
      image: PropTypes.string,
      thumbnail: PropTypes.string,
    })
  ),
  illustration: PropTypes.string,
  description: PropTypes.string,
  isOrganizer: PropTypes.bool,
  endTime: PropTypes.instanceOf(DateTime),
  routes: PropTypes.object,
  rsvp: PropTypes.string,
};

export default EventDescription;
