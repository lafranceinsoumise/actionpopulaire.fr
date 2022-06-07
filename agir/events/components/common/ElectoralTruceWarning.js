import { DateTime } from "luxon";
import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

const StyledDiscountWarning = styled.div`
  display: flex;
  flex-flow: row nowrap;
  align-items: flex-start;
  gap: 1rem;

  background-color: ${(props) => props.theme.primary100};
  border-radius: ${(props) => props.theme.borderRadius};
  color: ${(props) => props.theme.black1000};
  margin: 1.5rem 0;
  padding: 1.5rem;

  & > :first-child {
    color: ${(props) => props.theme.primary600};
    @media (max-width: 415px) {
      display: none;
    }
  }

  div {
    margin: 0;
    font-size: 1rem;
    line-height: 1.5;

    h5,
    strong {
      font-weight: 600;
    }

    h5 {
      margin: 0;
      padding: 0;
      line-height: 1;
      font-size: 18px;
    }
  }
`;

export const ElectoralTruceWarning = (props) => {
  const isActive = useMemo(
    () => DateTime.local() < DateTime.fromISO("2022-06-19T18:00:00.000Z"),
    []
  );

  if (!isActive) {
    return null;
  }

  return (
    <StyledDiscountWarning {...props}>
      <FeatherIcon name="alert-triangle" />
      <div>
        <h5>Trêve électorale</h5>
        <Spacer size="0.5rem" />
        Les weekend du 12 et 19 juin 2022, entre{" "}
        <strong>vendredi minuit</strong> (nuit entre vendredi et samedi) et{" "}
        <strong>dimanche 20h</strong>, seul les événements du type{" "}
        <strong>&laquo;&nbsp;Soirée&nbsp;électorale&nbsp;&raquo;</strong> seront
        autorisés sur Action Populaire.
      </div>
    </StyledDiscountWarning>
  );
};

export default ElectoralTruceWarning;
