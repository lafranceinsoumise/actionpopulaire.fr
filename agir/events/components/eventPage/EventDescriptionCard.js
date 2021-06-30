import React from "react";
import PropTypes from "prop-types";

import styled from "styled-components";

import { DateTime } from "luxon";
import Button from "@agir/front/genericComponents/Button";
import Collapsible from "@agir/front/genericComponents/Collapsible.js";
import Card from "@agir/front/genericComponents/Card";
import Spacer from "@agir/front/genericComponents/Spacer";

import style from "@agir/front/genericComponents/_variables.scss";

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

  img {
    margin: 10px 0px;
  }
`;

const StyledButton = styled(Button)`
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  border-radius: ${style.borderRadius};
  margin: 0 16px;
`;

const StyledActionButtons = styled.div`
  display: inline-grid;
  grid-gap: 0.5rem;
  grid-template-columns: auto auto;
  padding: 0.5rem 0;

  @media (max-width: ${style.collapse}px) {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(275px, 1fr));
  }

  ${Button} {
    margin: 0;
    justify-content: center;

    && *,
    && *::before {
      flex: 0 0 auto;
    }
  }

  ${Button} + ${Button} {
    margin-left: 0;
  }
`;

const StyledCard = styled(Card)`
  margin-bottom: 24px;
  overflow: hidden;
  border-bottom: 1px solid ${style.black50};
`;

const EventDescriptionCard = ({
  illustration,
  description,
  isOrganizer,
  endTime,
  routes,
}) => {
  return (
    <>
      {description ? (
        <StyledCard>
          <DescriptionSection>
            <b>L'événement</b>
            {illustration?.banner && (
              <DescriptionSection>
                <img
                  src={illustration.banner}
                  alt="Image d'illustration de l'événement postée par l'utilisateur"
                  style={{
                    maxWidth: "100%",
                    height: "auto",
                    maxHeight: "500px",
                    borderRadius: "8px",
                  }}
                />
              </DescriptionSection>
            )}

            <Collapsible
              dangerouslySetInnerHTML={{ __html: description }}
              fadingOverflow
            />
            <Spacer />
            {isOrganizer && endTime > DateTime.local() && (
              <StyledActionButtons>
                <StyledButton as="a" href={routes.edit}>
                  Modifier la description
                </StyledButton>

                <StyledButton as="a" href={routes.edit}>
                  Ajouter une image d'illustration
                </StyledButton>
              </StyledActionButtons>
            )}
          </DescriptionSection>
        </StyledCard>
      ) : null}

      {!description && isOrganizer && endTime > DateTime.local() && (
        <StyledCard>
          <DescriptionSection>
            <h2>Ajoutez une description !</h2>
            <p>
              Donner tous les informations nécessaires aux participants de votre
              événement. Comment accéder au lieu, quel est le programme, les
              liens pour être tenu au courant... Et ajoutez une image !
            </p>
            <div>
              <StyledButton as="a" href={routes.edit}>
                Ajouter une description
              </StyledButton>

              {!illustration?.banner && (
                <StyledButton as="a" href={routes.edit}>
                  Ajouter une image d'illustration
                </StyledButton>
              )}
            </div>
          </DescriptionSection>
        </StyledCard>
      )}
    </>
  );
};

EventDescriptionCard.propTypes = {
  compteRendu: PropTypes.string,
  compteRenduPhotos: PropTypes.arrayOf(
    PropTypes.shape({
      image: PropTypes.string,
      thumbnail: PropTypes.string,
    })
  ),
  illustration: PropTypes.shape({
    banner: PropTypes.string,
    thumbnail: PropTypes.string,
  }),
  description: PropTypes.string,
  isOrganizer: PropTypes.bool,
  endTime: PropTypes.instanceOf(DateTime),
  routes: PropTypes.object,
  rsvp: PropTypes.string,
};

export default EventDescriptionCard;
