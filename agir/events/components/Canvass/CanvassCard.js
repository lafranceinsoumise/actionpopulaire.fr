import React from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import logo from "./images/Canvass.png";

const StyledLogo = styled.div`
  width: 100%;
  height: 185px;
  background-repeat: no-repeat;
  background-color: #040408;
  background-image: url(${logo});
  background-position: center center;
  background-size: contain;

  @media (min-width: ${(props) => props.theme.collapse}px) {
    background-size: cover;

    ${(props) =>
      props.$flex &&
      `
      flex: 0 0 240px;
      width: 240px;
      height: 148px;
  `}
  }
`;

const StyledCard = styled.div`
  padding: 0;
  box-shadow: ${(props) => props.theme.cardShadow};
  border-radius: ${(props) => props.theme.borderRadius};
  overflow: hidden;

  @media (min-width: ${(props) => props.theme.collapse}px) {
    display: ${(props) => (props.$flex ? "flex" : "block")};
    font-size: ${(props) => (props.$flex ? "1rem" : "0.875rem")};
    align-items: center;
  }

  article {
    display: grid;
    gap: 1rem;
    padding: 1rem;
  }

  p {
    font-size: 0.875rem;
    font-weight: 700;
    margin: 0;
  }

  footer {
    display: flex;
    flex-direction: row wrap;
    gap: 0.5rem;
  }
`;

const CanvassCard = ({ flex = false, ...rest }) => (
  <StyledCard $flex={flex} {...rest}>
    <StyledLogo $flex={flex} aria-hidden="true" />
    <article>
      <p>
        Canvass vous propose un itinéraire de porte-à-porte à partir de son
        propre algorithme
      </p>
      <footer>
        <Button small link route="canvass" icon="external-link" iconRight>
          Ouvrir la carte
        </Button>
        <Button small link route="canvassHelp" icon="external-link" iconRight>
          En savoir plus
        </Button>
      </footer>
    </article>
  </StyledCard>
);

export default CanvassCard;
