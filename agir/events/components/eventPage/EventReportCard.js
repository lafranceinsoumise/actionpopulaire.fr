import { DateTime } from "luxon";
import React from "react";
import styled from "styled-components";
import Collapsible from "@agir/front/genericComponents/Collapsible";
import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import Spacer from "@agir/front/genericComponents/Spacer";
import style from "@agir/front/genericComponents/_variables.scss";
import { routeConfig } from "@agir/front/app/routes.config";

const StyledCard = styled(Card)`
  p {
    margin: 0;
  }

  margin-bottom: 24px;
  overflow: hidden;
  border-bottom: 1px solid ${style.black50};
`;

const EventReportCard = ({ id, compteRendu, isOrganizer, endTime, routes }) => {
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
      <Spacer size="0.5rem" />
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
        <Button
          style={{ marginTop: "1rem" }}
          link
          to={routeConfig.eventSettings.getLink({
            eventPk: id,
            activePanel: "compte-rendu",
          })}
        >
          {compteRendu ? "Modifier le" : "Ajouter un"} compte-rendu
        </Button>
      )}
    </StyledCard>
  );
};

export default EventReportCard;
