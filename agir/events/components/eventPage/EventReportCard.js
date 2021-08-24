import { DateTime } from "luxon";
import React from "react";
import styled from "styled-components";
import Collapsible from "../../../front/components/genericComponents/Collapsible";
import Button from "../../../front/components/genericComponents/Button";
import Card from "../../../front/components/genericComponents/Card";
import style from "@agir/front/genericComponents/_variables.scss";

const StyledCard = styled(Card)`
  p {
    margin: 0;
  }

  margin-bottom: 24px;
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
        <Button style={{ marginTop: "1rem" }} link href={routes.compteRendu}>
          {compteRendu ? "Modifier le" : "Ajouter un"} compte-rendu
        </Button>
      )}
    </StyledCard>
  );
};

export default EventReportCard;
