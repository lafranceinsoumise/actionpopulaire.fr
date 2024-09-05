import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import { parseDiscountCodes } from "@agir/groups/groupPage/utils";

import Button from "@agir/front/genericComponents/Button";
import Card from "./GroupPageCard";

const StyledList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0 0 1rem;

  &:empty {
    display: none;
  }

  li {
    &:first-child {
      margin-bottom: 0.25rem;
    }
  }
`;

const StyledCard = styled(Card)`
  padding: 1.5rem;
  border-radius: 0;

  && {
    background-color: ${(props) => props.theme.text25};

    @media (max-width: ${(props) => props.theme.collapse}px) {
      background-color: ${(props) => props.theme.background0};
    }
  }
`;

const GroupOrders = (props) => {
  const { isManager, discountCodes, routes } = props;
  const orderURL = routes && routes.orders;
  const [codes, specialCodes] = useMemo(
    () => parseDiscountCodes(discountCodes),
    [discountCodes],
  );

  return isManager ? (
    <StyledCard title="Commander du matériel">
      <StyledList>
        {specialCodes.map(({ label, code, expiration }) => (
          <li key={code}>
            <strong>🎟️&nbsp;{label}</strong>
            <br />
            {code} <span>(exp. {expiration})</span>
          </li>
        ))}
      </StyledList>
      <StyledList>
        {codes.map(({ code, expiration, month }) => (
          <li key={code}>
            <strong>Code du mois de {month}</strong>
            <br />
            {code} <span>(exp. {expiration})</span>
          </li>
        ))}
      </StyledList>
      {orderURL ? (
        <Button link href={orderURL} color="primary" small>
          Commander du matériel
        </Button>
      ) : null}
    </StyledCard>
  ) : null;
};

GroupOrders.propTypes = {
  discountCodes: PropTypes.arrayOf(
    PropTypes.shape({
      code: PropTypes.string,
      expiration: PropTypes.string,
    }),
  ),
  isManager: PropTypes.bool,
  routes: PropTypes.shape({
    orders: PropTypes.string,
  }),
};
export default GroupOrders;
