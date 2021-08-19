import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";

import { EVENT_PROJECT_STATUS } from "./config";

const StyledCard = styled.div`
  text-align: left;
  border-radius: ${(props) => props.theme.borderRadius};
  box-shadow: ${(props) => props.theme.cardShadow};
  width: 100%;
  padding: 1rem;
  margin: 0;

  h4 {
    margin: 0;
    padding: 0 0 0.5rem;
    font-size: 1rem;
    line-height: 1.5;
    font-weight: 600;
    color: ${(props) =>
      props.$pending ? props.theme.green500 : props.theme.black700};
  }

  p {
    margin: 0;
    padding: 0;
    font-size: 0.875rem;
    font-weight: 400;
    line-height: 1.6;
  }
`;

const ProjectStatusCard = (props) => {
  const { status, hasRequiredDocuments, hasMissingDocuments } = props;

  const step = EVENT_PROJECT_STATUS[status];

  if (!hasRequiredDocuments) {
    return (
      <StyledCard $pending>
        <h4>Votre événement privé ne nécessite pas de documents</h4>
        <p>
          Vous avez changé le type de l’événement. Dans le cadre d’un événement
          privé, vous n’avez pas besoin d’envoyer de document.
        </p>
      </StyledCard>
    );
  }

  if (step === "pending" && !hasMissingDocuments) {
    return (
      <StyledCard $pending>
        <h4>Vos documents sont en relecture par le secrétariat général</h4>
        <p>
          Vous pouvez en ajouter encore autant que nécessaire jusqu’à leur
          relecture.
        </p>
      </StyledCard>
    );
  }

  if (step === "archived") {
    return (
      <StyledCard>
        <h4>Événement archivé</h4>
        <p>
          Le secrétariat général a relu et validé les documents de votre
          événement
        </p>
      </StyledCard>
    );
  }

  if (step === "refused") {
    return (
      <StyledCard>
        <h4>Événement public refusé</h4>
        <p>
          Veuillez prendre contact avec le secréatariat général pour plus
          d’informations
        </p>
      </StyledCard>
    );
  }

  return null;
};

ProjectStatusCard.propTypes = {
  status: PropTypes.string,
  hasRequiredDocuments: PropTypes.bool,
  hasMissingDocuments: PropTypes.bool,
};

export default ProjectStatusCard;
