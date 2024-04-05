import React from "react";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

import sunIcon from "@agir/activity/images/sunIcon.svg";

export const StyledEmptyList = styled.p`
  margin: 0;
  padding: 32px 24px;
  display: flex;
  flex-flow: row nowrap;
  align-items: stretch;
  border: 1px solid ${style.black100};
  margin: 32px 0;

  @media (max-width: ${style.collapse}px) {
    margin: 24px 16px;
  }

  &::before {
    content: "";
    display: block;
    background-repeat: no-repeat;
    background-position: center left;
    background-size: contain;
    background-image: url(${sunIcon});
    flex: 0 0 50px;
    margin-right: 22px;
  }

  span {
    margin: 0;
    padding: 0;
    flex: 1 1 auto;
  }
`;

export const EmptyActivityList = () => {
  return (
    <StyledEmptyList>
      <span>
        Vous n’avez rien reçu ici.
        <br />
        Revenez plus tard !
      </span>
    </StyledEmptyList>
  );
};
export default EmptyActivityList;
