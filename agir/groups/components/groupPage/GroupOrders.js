import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

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
  && {
    background-color: ${style.black25};

    @media (max-width: ${style.collapse}px) {
      background-color: white;
    }
  }
`;

const GroupOrders = (props) => {
  const { isManager, discountCodes, routes } = props;
  const orderURL = routes && routes.orders;
  const [codes, specialCodes] = useMemo(
    () => parseDiscountCodes(discountCodes),
    [discountCodes]
  );

  return isManager ? (
    <StyledCard title="Commander du matériel" outlined>
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
    })
  ),
  isManager: PropTypes.bool,
  routes: PropTypes.shape({
    orders: PropTypes.string,
  }),
};
export default GroupOrders;
