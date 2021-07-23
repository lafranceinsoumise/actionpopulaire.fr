import React from "react";
import styled from "styled-components";

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
    color: ${(props) => props.theme.green500};
  }

  p {
    margin: 0;
    padding: 0;
    font-size: 0.875rem;
    font-weight: 400;
    line-height: 1.6;
  }
`;

const NoRequiredDocumentCard = () => {
  return (
    <StyledCard $pending>
      <h4>Votre événement privé ne nécessite pas de documents</h4>
      <p>
        Vous avez changé le type de l’événement. Dans le cadre d’un événement
        privé, vous n’avez pas besoin d’envoyer de document.
      </p>
    </StyledCard>
  );
};

export default NoRequiredDocumentCard;
