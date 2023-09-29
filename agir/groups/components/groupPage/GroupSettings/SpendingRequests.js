import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import Link from "@agir/front/app/Link";
import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import {
  CATEGORY_OPTIONS,
  FALLBACK_CATEGORY,
} from "@agir/donations/spendingRequest/common/form.config";
import { STATUS_CONFIG } from "@agir/donations/spendingRequest/common/SpendingRequestStatus";
import { useIsDesktop } from "@agir/front/genericComponents/grid";

const StyledSpendingRequest = styled(Link)`
  display: flex;
  flex-flow: row nowrap;
  justify-content: space-between;
  align-items: start;
  gap: 1rem;
  padding: 1rem;
  box-shadow: ${(props) => props.theme.cardShadow};
  border-radius: ${(props) => props.theme.borderRadius};
  font-size: 1rem;

  @media (max-width: 360px) {
    gap: 0.5rem;
    font-size: 0.875rem;
  }

  &,
  &:hover,
  &:focus {
    color: ${(props) => props.theme.black1000};
    text-decoration: none;
  }

  & > * {
    flex: 0 0 auto;
  }

  ${RawFeatherIcon} {
    margin-top: 0.1875rem;
    width: 3rem;
    height: 3rem;
    border-radius: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: ${(props) =>
      props.theme[props.$status.color] ||
      props.$status.color ||
      props.theme.white}11;
    color: ${(props) =>
      props.theme[props.$status.color] ||
      props.$status.color ||
      "currentcolor"};

    & > * {
      flex: 0 0 auto;
    }

    @media (max-width: 360px) {
      width: 2rem;
      height: 2rem;
    }

    svg {
      width: 1.5rem;
      height: 1.5rem;

      @media (max-width: 360px) {
        width: 1rem;
        height: 1rem;
      }
    }
  }

  ${RawFeatherIcon} + span {
    flex: 1 1 auto;
    padding-right: 1rem;
    display: flex;
    flex-flow: column nowrap;
    align-items: start;
    gap: 0.25rem;
    min-width: 0;

    & > * {
      margin: 0;
      padding: 0;
    }

    strong {
      font-weight: 700;
      line-height: 1.5;
    }

    small {
      font-size: 0.75em;
      line-height: 2;
      font-weight: 600;
      text-transform: uppercase;
      color: ${(props) => props.theme.black500};
      border: 1px solid ${(props) => props.theme.black50};
      border-radius: 0.25rem;
      padding: 0 0.5rem;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
      max-width: 100%;
    }
  }

  ${Button} {
    @media (max-width: 360px) {
      display: none;
    }
  }
`;
const StyledSpendingRequests = styled.div`
  ul {
    list-style: none;
    padding: 0;
    margin: 0 0 1rem;
    display: flex;
    flex-flow: column nowrap;
    gap: 1rem;
  }

  & > ${Button} {
    justify-content: flex-start;
    text-align: left;
  }
`;

const SpendingRequest = (props) => {
  const { id, title } = props;

  const isDesktop = useIsDesktop();
  const status = useMemo(() => STATUS_CONFIG[props.status], [props.status]);
  const category = useMemo(
    () =>
      CATEGORY_OPTIONS[props.category] || {
        ...FALLBACK_CATEGORY,
        value: props.category,
      },
    [props.category],
  );

  return (
    <StyledSpendingRequest
      route="spendingRequestDetails"
      routeParams={{ spendingRequestPk: id }}
      aria-label="Voir la demande"
      $status={status}
    >
      <RawFeatherIcon
        title={category.label}
        name={category.icon}
        width="1.5rem"
        height="1.5rem"
      />
      <span>
        <strong>{title}</strong>
        <small title={status.shortLabel || status.label}>
          {status.shortLabel || status.label}
        </small>
      </span>
      <Button color="secondary" small={!isDesktop}>
        Voir
      </Button>
    </StyledSpendingRequest>
  );
};

SpendingRequest.propTypes = {
  id: PropTypes.string,
  title: PropTypes.string,
  status: PropTypes.string,
  date: PropTypes.string,
  category: PropTypes.string,
};

const SpendingRequests = ({ groupPk, spendingRequests }) => {
  return (
    <StyledSpendingRequests>
      {groupPk && (
        <Button
          link
          icon="plus"
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
    PropTypes.shape(SpendingRequest.propTypes),
  ),
};
export default SpendingRequests;
