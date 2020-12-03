import React from "react";
import PropTypes from "prop-types";

import styled from "styled-components";

import { Column, Row } from "@agir/front/genericComponents/grid";
import { DateTime } from "luxon";
import Button from "@agir/front/genericComponents/Button";
import Collapsible from "@agir/front/genericComponents/Collapsible.js";

const DescriptionSection = styled.div`
  margin: 0 0 2rem;

  &:empty {
    margin: 0;
  }

  & > * {
    margin-top: 0;
    margin-bottom: 1rem;

    &:empty {
      margin-bottom: 0;
    }
  }

  h2 {
    font-size: 1.25rem;
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
        compteRenduPhotos.length > 0 || rsvp ? (
          <DescriptionSection>
            <h2>Photos de l'événement</h2>
            {compteRenduPhotos.length > 0 ? (
              <Row gutter={12}>
                {compteRenduPhotos.map((url, key) => (
                  <Column collapse={500} key={key} width={["50%", "content"]}>
                    <img
                      src={url}
                      alt="Photo de l'événement postée par l'utilisateur"
                    />
                  </Column>
                ))}
              </Row>
            ) : (
              <p>Il n'y a pas encore de photo de cet évènement.</p>
            )}
            {!!rsvp && (
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
            <p>Il n'y a pas encore de compte-rendu de cet évènement.</p>
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
  compteRenduPhotos: PropTypes.arrayOf(PropTypes.string),
  illustration: PropTypes.string,
  description: PropTypes.string,
  isOrganizer: PropTypes.bool,
  endTime: PropTypes.instanceOf(DateTime),
  routes: PropTypes.object,
  rsvp: PropTypes.string,
};

export default EventDescription;
