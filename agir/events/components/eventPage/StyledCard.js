import styled from "styled-components";

import Card from "@agir/front/genericComponents/Card";

const StyledCard = styled(Card)`
  padding: 1.5rem;
  margin: 2rem 0;
  border-bottom: 1px solid ${(props) => props.theme.text50};
  border-radius: ${(props) => props.theme.borderRadius};
  background-color: ${(props) => props.theme.background0};

  @media (max-width: ${(props) => props.theme.collapse}px) {
    margin: 0;
  }

  h5,
  p {
    margin: 0;
    padding: 0;
  }

  h5 {
    font-size: 1.125rem;
    font-weight: 600;
    line-height: 1.5;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 0.875rem;
      font-weight: 700;
    }
  }

  p {
    font-size: 1rem;
    line-height: 1.6;
    padding: 0.25rem 0 0;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 0.875rem;
    }
  }
`;

export default StyledCard;
