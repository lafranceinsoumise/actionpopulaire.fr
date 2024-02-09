import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

export const StyledContainer = styled.div`
  width: 100%;
  max-width: 1100px;
  display: flex;
  flex-direction: column;
  margin: 0 auto;
  padding: 20px 50px 3rem;

  @media (max-width: ${style.collapse}px) {
    padding: 20px 12px 3rem;
  }

  h3 {
    font-size: 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;

    span {
      font-weight: normal;
    }
  }
`;

export const StyledFilters = styled.div`
  display: flex;

  @media (max-width: ${style.collapse}px) {
    flex-direction: column;
  }

  & > label {
    flex: 1;
    margin-right: 10px;

    &&:last-child {
      margin-right: 0;
    }

    @media (max-width: ${style.collapse}px) {
      margin-right: 0;
      margin-bottom: 1rem;
    }
  }
`;
