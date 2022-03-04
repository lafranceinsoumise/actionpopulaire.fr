import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

import {
  sendVotingProxyInformation,
  confirmVotingProxyRequests,
} from "@agir/voting_proxies/Common/api";

const StyledWidget = styled.div`
  background-color: ${({ theme }) => theme.primary50};
  border-radius: ${({ theme }) => theme.borderRadius};
  padding: 1.5rem;

  ${Button} {
    text-align: left;
    line-height: 1.2;
  }

  footer {
    padding: 1rem 0 0;
    margin: 0;
    font-size: 1rem;
    color: ${({ theme }) => theme.redNSP};
  }
`;

const VotingProxyWidget = (props) => {
  const { firstName, votingDates, votingProxyRequests } = props;

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState("");
  const [isConfirmed, setIsConfirmed] = useState(
    votingProxyRequests.every((request) => request.status === "confirmed")
  );

  const sendInformation = useCallback(async () => {
    setError("");
    setIsLoading("info");
    const result = await sendVotingProxyInformation(votingProxyRequests);
    setIsLoading(false);
    if (result.error) {
      setError(result.error);
    }
  }, [votingProxyRequests]);

  const confirm = useCallback(async () => {
    setError("");
    setIsLoading("confirm");
    const result = await confirmVotingProxyRequests(votingProxyRequests);
    setIsLoading(false);
    if (result.error) {
      setError(result.error);
    } else {
      setIsConfirmed(true);
    }
  }, [votingProxyRequests]);

  return (
    <StyledWidget>
      <p>
        <strong>Prénom(s)&nbsp;:</strong>
        <br />
        {firstName}
      </p>
      <p>
        <strong>Scrutin{votingDates.length > 1 && "s"}&nbsp;:</strong>
        <br />
        {votingDates.map((date) => (
          <span key={date}>
            {date}
            <br />
          </span>
        ))}
      </p>
      <Spacer size="1rem" />
      <p>
        {!isConfirmed && (
          <Button
            disabled={!!isLoading}
            loading={isLoading === "info"}
            small
            wrap
            color="primary"
            onClick={sendInformation}
            icon="message-square"
          >
            Recevoir par SMS les informations pour établir la procuration
          </Button>
        )}
        <Spacer size=".5rem" />
        <Button
          disabled={!!isLoading || isConfirmed}
          loading={isLoading === "confirm"}
          small
          wrap
          color="primary"
          onClick={confirm}
          icon="check-square"
        >
          {isConfirmed
            ? "Procuration validée"
            : "Prévenir la personne que la procuration a été établie"}
        </Button>
      </p>
      {error && <footer>{error}</footer>}
    </StyledWidget>
  );
};
VotingProxyWidget.propTypes = {
  firstName: PropTypes.string.isRequired,
  votingDates: PropTypes.arrayOf(PropTypes.string).isRequired,
  votingProxyRequests: PropTypes.arrayOf(PropTypes.string).isRequired,
};
export default VotingProxyWidget;
