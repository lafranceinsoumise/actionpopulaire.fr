import { DateTime } from "luxon";
import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";
import StyledCard from "./StyledCard";

import { useResponsiveMemo } from "@agir/front/genericComponents/grid";
import { routeConfig } from "@agir/front/app/routes.config";

const DescriptionSection = styled.div`
  margin: 0;

  & > img {
    max-width: 100%;
    height: auto;
    max-height: 500px;
    border-radius: ${(props) => props.theme.borderRadius};
    margin-bottom: 1rem;
  }

  & > p {
    color: ${(props) => props.theme.text700};
  }
`;

const StyledActionButtons = styled.div`
  display: inline-grid;
  grid-gap: 0.5rem;
  grid-template-columns: auto auto;
  padding: 1rem 0 0;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(275px, 1fr));
  }
`;

const StyleDescriptionCard = styled(StyledCard)`
  margin-bottom: 24px;
  overflow: hidden;
  border-bottom: 1px solid ${(props) => props.theme.text50};
`;

const EventDescriptionCard = ({
  id,
  illustration,
  description,
  isOrganizer,
  isEditable,
  endTime,
}) => {
  const image = useResponsiveMemo(null, illustration?.banner);
  const canEdit = isEditable && isOrganizer && endTime > DateTime.local();

  if (!description && !image && !canEdit) {
    return null;
  }

  return (
    <StyleDescriptionCard>
      <DescriptionSection>
        <h5>L'événement</h5>

        <Spacer size="1rem" />

        <DescriptionSection>
          {image && (
            <img
              src={image}
              alt="Image d'illustration de l'événement postée par l'utilisateur"
            />
          )}
          {description ? (
            <div dangerouslySetInnerHTML={{ __html: description }} />
          ) : (
            canEdit && (
              <p>
                <strong>Ajoutez une description !</strong> Donner tous les
                informations nécessaires aux participants de votre événement.
                Comment accéder au lieu, quel est le programme, les liens pour
                être tenu au courant... {!image && "Et ajoutez une image\xa0!"}
              </p>
            )
          )}
        </DescriptionSection>

        {canEdit && (
          <StyledActionButtons>
            <Button
              link
              to={routeConfig.eventSettings.getLink({ eventPk: id })}
            >
              {description ? "Modifier la" : "Ajouter une"} description
            </Button>
            <Button
              link
              to={routeConfig.eventSettings.getLink({ eventPk: id })}
            >
              {image ? "Changer l'" : "Ajouter une "}image d'illustration
            </Button>
          </StyledActionButtons>
        )}
      </DescriptionSection>
    </StyleDescriptionCard>
  );
};

EventDescriptionCard.propTypes = {
  illustration: PropTypes.shape({
    banner: PropTypes.string,
  }),
  description: PropTypes.string,
  isEditable: PropTypes.bool,
  isOrganizer: PropTypes.bool,
  endTime: PropTypes.any,
  routes: PropTypes.shape({
    edit: PropTypes.string,
  }),
};

export default EventDescriptionCard;
