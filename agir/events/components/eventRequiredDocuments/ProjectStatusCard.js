import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";

import { EVENT_PROJECT_STATUS } from "./config";

const StyledCard = styled.figure`
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
  const { status } = props;

  if (status === EVENT_PROJECT_STATUS.pending) {
    return (
      <StyledCard $pending>
        <h4>Vos documents sont en relecture par le secrétariat général</h4>
        <p>
          Vous pouvez en ajouter encore en cliquant sur le bouton ci-dessous.
        </p>
      </StyledCard>
    );
  }

  if (status === EVENT_PROJECT_STATUS.archived) {
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

  return null;
};

ProjectStatusCard.propTypes = {
  status: PropTypes.string,
};

export default ProjectStatusCard;
