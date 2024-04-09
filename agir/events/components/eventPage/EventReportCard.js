import { DateTime } from "luxon";
import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Collapsible from "@agir/front/genericComponents/Collapsible";
import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import Spacer from "@agir/front/genericComponents/Spacer";
import StyledCard from "./StyledCard";
import * as style from "@agir/front/genericComponents/_variables.scss";

import { routeConfig } from "@agir/front/app/routes.config";

const EventReportCard = ({
  id,
  compteRendu,
  isOrganizer,
  isEditable,
  endTime,
}) => {
  if (!compteRendu && !isOrganizer) {
    return null;
  }

  return (
    <StyledCard>
      <h5>Compte rendu</h5>
      <Spacer size="0.5rem" />
      {compteRendu ? (
        <Collapsible
          dangerouslySetInnerHTML={{ __html: compteRendu }}
          style={{ margin: "1em 0 3em" }}
          fadingOverflow
        />
      ) : (
        <p>Il n'y a pas encore de compte rendu de cet événement.</p>
      )}
      {isEditable && isOrganizer && (
        <Button
          style={{ marginTop: "1rem" }}
          link
          to={routeConfig.eventSettings.getLink({
            eventPk: id,
            activePanel: "compte-rendu",
          })}
        >
          {compteRendu ? "Modifier le" : "Ajouter un"} compte rendu
        </Button>
      )}
    </StyledCard>
  );
};

EventReportCard.propTypes = {
  id: PropTypes.string,
  compteRendu: PropTypes.string,
  isEditable: PropTypes.bool,
  isOrganizer: PropTypes.bool,
  endTime: PropTypes.object,
};
export default EventReportCard;
