import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import { parseDiscountCodes } from "@agir/groups/groupPage/utils";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRouteById } from "@agir/front/globalContext/reducers";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Card from "./GroupPageCard";

const StyledList = styled.ul`
  list-style: none;
  padding: 0;
  margin: 0 0 1rem;

  li {
    &:first-child {
      margin-bottom: 0.25rem;
    }
  }
`;

const StyledCard = styled(Card)`
  @media (min-width: ${style.collapse}px) {
    padding: 1.5rem;
    border: 1px solid ${style.black200};
  }
`;

const GroupOrders = (props) => {
  const { isManager, discountCodes } = props;
  const orderURL = useSelector((state) => getRouteById(state, "materiel"));
  const codes = useMemo(() => parseDiscountCodes(discountCodes), [
    discountCodes,
  ]);

  return isManager ? (
    <StyledCard title="Commander du matériel">
      {Array.isArray(codes) && codes.length > 0 ? (
        <StyledList>
          <li>Codes de réduction :</li>
          {codes.map(({ code, expiration }) => (
            <li key={code}>
              {code} <span>(exp. {expiration})</span>
            </li>
          ))}
        </StyledList>
      ) : null}
      {orderURL ? (
        <Button as="a" href={orderURL} color="primary" small inline>
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
      expirationDate: PropTypes.string,
    })
  ),
  isManager: PropTypes.bool,
};
export default GroupOrders;
