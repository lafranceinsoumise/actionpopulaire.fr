import { DateTime } from "luxon";
import React from "react";
import styled from "styled-components";
import Collapsible from "../../../front/components/genericComponents/Collapsible";
import Button from "../../../front/components/genericComponents/Button";
import Card from "../../../front/components/genericComponents/Card";
import style from "@agir/front/genericComponents/_variables.scss";

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

  margin-bottom: 24px;
  box-shadow: ${style.cardShadow};
  border-radius: ${style.borderRadius};
  overflow: hidden;
  border-bottom: 1px solid ${style.black50};
`;

const EventReportCard = ({ compteRendu, isOrganizer, endTime, routes }) => {
  const isPast = endTime < DateTime.local();

  if (!isPast) {
    return null;
  }

  if (!compteRendu && !isOrganizer) {
    return null;
  }
  
  return (
    <StyledCard>
      <b>Compte-rendu</b>
      {compteRendu ? (
        <Collapsible
          dangerouslySetInnerHTML={{ __html: compteRendu }}
          style={{ margin: "1em 0 3em" }}
          fadingOverflow
        />
      ) : (
        <p>Il n'y a pas encore de compte-rendu de cet événement.</p>
      )}
      {isOrganizer && (
        <StyledButton as="a" href={routes.compteRendu}>
          {compteRendu ? "Modifier le" : "Ajouter un"} compte-rendu
        </StyledButton>
      )}
    </StyledCard>
  );
};

export default EventReportCard;
