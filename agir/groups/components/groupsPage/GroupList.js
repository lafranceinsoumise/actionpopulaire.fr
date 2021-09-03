import styled from "styled-components";

import Card from "@agir/front/genericComponents/Card";

const GroupList = styled.article`
  padding: 0;

  & > ${Card} {
    margin-bottom: 1rem;
    border: none;
    box-shadow: ${(props) => props.theme.cardShadow};
    border-radius: ${(props) => props.theme.borderRadius};

    @media (max-width: ${(props) => props.theme.collapse}px) {
      padding: 1rem 1.5rem;
      box-shadow: ${(props) => props.theme.elaborateShadow};
    }
  }

  & > h3 {
    margin: 0;
    padding: 1.5rem 0;
    font-size: 1.625rem;
    line-height: 1.5;
    font-weight: 700;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      padding: 0.5rem 1.5rem 1rem;
      font-size: 1.125rem;
      font-weight: 500;
      line-height: 1.4;
    }
  }
`;

export default GroupList;
