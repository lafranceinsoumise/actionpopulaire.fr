import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { displayPrice } from "@agir/lib/utils/display";

const StyledAmountInformations = styled.div`
  padding: 1rem;
  background-color: ${(props) => props.theme.primary100};
  color: ${(props) => props.theme.primary500};
  border-radius: 4px;
  ul {
    margin: 0;
  }
`;

const AmountInformations = (props) => {
  const { groupName, totalAmount, groupAmount, nationalAmount } = props;
  if (!groupName || !groupAmount) {
    return null;
  }

  return (
    <StyledAmountInformations>
      Je fais un don de <b>{displayPrice(totalAmount)}</b> qui sera réparti :
      <br />
      <ul>
        <li>
          <b>{displayPrice(groupAmount)}</b> pour le groupe {groupName}
        </li>
        <li>
          <b>{displayPrice(nationalAmount)}</b> pour les activités nationales
        </li>
      </ul>
    </StyledAmountInformations>
  );
};

AmountInformations.propTypes = {
  groupName: PropTypes.object,
  totalAmount: PropTypes.number,
  groupAmount: PropTypes.number,
  nationalAmount: PropTypes.number,
};

export default AmountInformations;
