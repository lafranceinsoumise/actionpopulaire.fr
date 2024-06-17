import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import FaIcon from "@agir/front/genericComponents/FaIcon";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledFaIcon = styled(FaIcon)``;
const StyledFeatherIcon = styled(RawFeatherIcon)``;
const StyledRequestCard = styled.div`
  display: grid;
  grid-template-columns: 1fr auto;
  align-items: start;
  gap: 1rem;
  padding: 1rem;
  background-color: ${({ theme }) => theme.white};
  border-radius: ${({ theme }) => theme.borderRadius};
  border: 1px solid ${({ theme }) => theme.black100};

  @media (max-width: ${(props) => props.theme.collapse}px) {
    grid-template-columns: 1fr;
  }

  p {
    margin: 0;
    padding: 0;
    display: flex;
    align-items: start;
    line-height: 1.5;
    gap: 0.5rem;
    margin-top: 0.5rem;
    font-size: 1rem;

    ${StyledFaIcon},
    ${StyledFeatherIcon} {
      line-height: 1.5;
      color: ${(props) => props.theme.primary500};
    }

    ${StyledFaIcon}  {
      padding-left: 0.125rem;
      margin-right: 0.4rem;
    }

    & > strong {
      text-transform: capitalize;
      font-weight: 400;
      font-size: 0.875rem;
    }
  }

  p:first-child > strong {
    margin-top: 0;
    font-weight: 700;
    font-size: 1rem;
  }
`;

const StyledWrapper = styled.div`
  h2,
  p {
    &::first-letter {
      text-transform: capitalize;
    }
  }

  footer {
    display: flex;
    gap: 1rem;
  }
`;

const RequestCard = (props) => {
  const {
    firstName,
    commune,
    consulate,
    pollingStationLabel,
    votingDates,
    replyURL,
  } = props;

  const first = useMemo(
    () =>
      firstName
        .replaceAll(",", " ")
        .replaceAll(/\s{2,}/g, " ")
        .split(" ")[0]
        .trim(),
    [firstName],
  );

  const dates = useMemo(
    () =>
      votingDates
        .map((date) => new Date(date).toLocaleString().slice(0, 10))
        .join(", "),
    [votingDates],
  );

  return (
    <StyledRequestCard>
      <div>
        {commune && (
          <p>
            <StyledFeatherIcon name="map-pin" />
            <strong>{commune}</strong>
          </p>
        )}
        {consulate && (
          <p>
            <StyledFeatherIcon name="map-pin" />
            <strong>{consulate}</strong>
          </p>
        )}
        {pollingStationLabel && (
          <p>
            <StyledFaIcon icon="booth-curtain:regular" size="1rem" />
            <strong>Bureau de vote&nbsp;: {pollingStationLabel}</strong>
          </p>
        )}
        {firstName && (
          <p>
            <StyledFeatherIcon name="user" />
            <strong>{firstName}</strong>
          </p>
        )}
        <p>
          <StyledFeatherIcon name="calendar" />
          <strong>{dates}</strong>
        </p>
      </div>
      <Button
        inline
        small
        link
        color="success"
        icon="arrow-right"
        to={replyURL}
      >
        Voter pour {first}
      </Button>
    </StyledRequestCard>
  );
};

RequestCard.propTypes = {
  ids: PropTypes.arrayOf(PropTypes.string),
  firstName: PropTypes.string,
  votingDates: PropTypes.arrayOf(PropTypes.string),
  pollingStationLabel: PropTypes.string.isRequired,
  commune: PropTypes.string,
  consulate: PropTypes.string,
  replyURL: PropTypes.string,
};

export default RequestCard;
