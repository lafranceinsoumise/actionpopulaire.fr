import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Link from "@agir/front/app/Link";
import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

const StyledSpendingRequest = styled(Link)`
  display: flex;
  flex-flow: row nowrap;
  justify-content: space-between;
  align-items: flex-start;
  padding: 0.5rem 0 1rem;
  border-top: 1px solid ${(props) => props.theme.black100};

  @media (max-width: ${(props) => props.theme.collapse}px) {
    flex-flow: column nowrap;
    justify-content: flex-start;
  }

  &,
  &:hover,
  &:focus {
    color: ${(props) => props.theme.black1000};
    text-decoration: none;
  }

  & > span,
  & > ${Button} {
    flex: 0 0 auto;
    margin-top: 0.5rem;
  }

  & > span:first-child {
    flex: 1 1 auto;
    padding-right: 1rem;
    display: flex;
    flex-flow: column nowrap;
    font-size: 0.875rem;

    & > * {
      margin: 0;
      padding: 0;
    }

    strong {
      font-size: 1rem;
      font-weight: 500;
    }

    span {
      font-size: inherit;
      color: ${(props) => props.theme.primary500};
      margin: 0.25rem 0;
    }

    small {
      font-size: inherit;
      font-weight: 400;
      color: ${(props) => props.theme.black700};
    }
  }
`;
const StyledSpendingRequests = styled.div`
  ul {
    list-style: none;
    padding: 0;
    margin: 0 0 1rem;
  }

  & > ${Button} {
    justify-content: flex-start;
    text-align: left;
  }
`;

const SpendingRequest = (props) => {
  const { id, title, status, date } = props;
  return (
    <StyledSpendingRequest
      route="spendingRequestDetails"
      routeParams={{ spendingRequestPk: id }}
      aria-label="Voir la demande"
    >
      <span>
        <strong>{title}</strong>
        <span>{date.slice(0, 10).split("-").reverse().join("/")}</span>
        <small>{status}</small>
      </span>
      <Button color="default" small>
        Voir la demande
      </Button>
    </StyledSpendingRequest>
  );
};

SpendingRequest.propTypes = {
  id: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  status: PropTypes.string.isRequired,
  date: PropTypes.string.isRequired,
};

const SpendingRequests = ({ groupPk, spendingRequests }) => {
  return (
    <StyledSpendingRequests>
      {groupPk && (
        <Button
          link
          icon="mail"
          route="createGroupSpendingRequest"
          routeParams={{ groupPk }}
          color="secondary"
          wrap
        >
          Créer une demande de dépense
        </Button>
      )}
      <Spacer size="1rem" />
      {Array.isArray(spendingRequests) && spendingRequests.length > 0 && (
        <ul>
          {spendingRequests.map((spendingRequest) => (
            <li key={spendingRequest.id}>
              <SpendingRequest {...spendingRequest} />
            </li>
          ))}
        </ul>
      )}
    </StyledSpendingRequests>
  );
};

SpendingRequests.propTypes = {
  groupPk: PropTypes.string,
  spendingRequests: PropTypes.arrayOf(
    PropTypes.shape(SpendingRequest.propTypes)
  ),
};
export default SpendingRequests;
