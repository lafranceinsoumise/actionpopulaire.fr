import React from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

const StyledWarning = styled.div`
  padding: 1.5rem;
  margin: 1rem 0 0;
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.5rem;
  background-color: ${(props) => props.theme.primary50};

  @media (max-width: ${(props) => props.theme.collapse}px) {
    display: flex;
    flex-direction: column;
    margin: 1rem -1.5rem;
  }

  & > p {
    grid-column: span 2;
    font-size: 0.875rem;

    strong {
      font-size: 1rem;
      line-height: 1.5;
    }

    em {
      font-style: normal;
      font-weight: 500;
      box-shadow: inset 0px -3px 0px ${(props) => props.theme.primary150};
    }
  }
`;

const TreveEventWarning = () => {
  if (Date.now() >= new Date("2024-06-09 20:00:00+0200").valueOf()) {
    return null;
  }

  return (
    <StyledWarning>
      <p>
        <strong>Trève électorale</strong>
        <Spacer size="0.5rem" />
        La veille d'une élection, la loi interdit de faire campagne. Vous ne
        pouvez pas organiser d'action en but de récolter des suffrages
        (porte-à-porte, tractage, réunion publique...). Pendant le weekend,
        seuls les événements des types suivants sont donc autorisés :{" "}
        <em>départ commun pour une manifestation/un rassemblement</em>,{" "}
        <em>soutien à une manifestation, un rassemblement</em> et{" "}
        <em>soirée électorale</em>.
      </p>
      <Button
        color="primary"
        small
        link
        wrap
        href="https://infos.actionpopulaire.fr/que-faire-le-9-juin/"
      >
        Que faire le jour de l'élection ?
      </Button>
      <Button
        small
        link
        href="https://www.service-public.fr/particuliers/vosdroits/services-en-ligne-et-formulaires/ISE"
      >
        Trouver mon bureau de vote
      </Button>
    </StyledWarning>
  );
};

export default TreveEventWarning;
