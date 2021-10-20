import React from "react";

import styled from "styled-components";
import Spacer from "@agir/front/genericComponents/Spacer";

const StyledAmountInformations = styled.div`
  padding: 1rem;
  background-color: ${(props) => props.theme.primary100};
  color: ${(props) => props.theme.primary500};
  border-radius: 4px;
  ul {
    margin: 0;
  }
`;

const AmountInformations = ({ group, total, amountGroup, amountNational }) => {
  if (!group?.id) {
    return <></>;
  }

  return (
    <>
      <StyledAmountInformations>
        Je fais un don de <b>{total}</b> qui sera réparti :
        <br />
        <ul>
          <li>
            <b>{amountGroup}</b> pour le groupe {group?.name}
          </li>
          <li>
            <b>{amountNational}</b> pour les activités nationales
          </li>
        </ul>
      </StyledAmountInformations>
      <Spacer size="1rem" />
    </>
  );
};

export default AmountInformations;
