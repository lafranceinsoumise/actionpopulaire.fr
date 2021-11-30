import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Link from "@agir/front/app/Link";

import { routeConfig } from "@agir/front/app/routes.config";
import { displayHumanDateString } from "@agir/lib/utils/time";

const StyledCard = styled(Link)`
  display: block;
  width: 254px;
  min-height: 74px;
  padding: 1rem;
  border-radius: ${(props) => props.theme.borderRadius};
  box-shadow: ${(props) => props.theme.cardShadow};
  background-color: white;

  &:hover,
  &:focus {
    text-decoration: none;
  }

  & + & {
    margin-top: 0.5rem;
  }

  & > * {
    font-size: 0.875rem;
    line-height: 1.5;
    font-weight: 500;
    display: block;
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;

    &::first-letter {
      text-transform: capitalize;
    }
  }
`;

export const MiniEventCard = (props) => {
  const { id, name, startTime } = props;
  return (
    <StyledCard to={routeConfig.eventDetails.getLink({ eventPk: id })}>
      <strong>{displayHumanDateString(startTime)}</strong>
      <span
        css={`
          color: ${(props) => props.theme.black1000};
        `}
      >
        {name}
      </span>
    </StyledCard>
  );
};

MiniEventCard.propTypes = {
  id: PropTypes.string.isRequired,
  startTime: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
};

export default MiniEventCard;
