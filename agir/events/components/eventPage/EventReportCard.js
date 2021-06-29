import { DateTime } from "luxon";
import React from "react";
import styled from "styled-components";
import Collapsible from "../../../front/components/genericComponents/Collapsible";
import Button from "../../../front/components/genericComponents/Button";
import Card from "../../../front/components/genericComponents/Card";

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

const EventReportCard = ({ compteRendu, isOrganizer, endTime, routes }) => {
  const isPast = endTime < DateTime.local();

  return (
    <>
      {isPast && (compteRendu || isOrganizer) ? (
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
          {isOrganizer && endTime < DateTime.local() && (
            <StyledButton as="a" href={routes.compteRendu}>
              {compteRendu ? "Modifier le" : "Ajouter un"} compte-rendu
            </StyledButton>
          )}
        </StyledCard>
      ) : null}
    </>
  );
};

export default EventReportCard;
