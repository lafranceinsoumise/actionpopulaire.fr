import React from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";

import background from "./images/TokTokBG.jpg";
import logo from "./images/TokTok.svg";

const StyledLogo = styled.div`
  width: 100%;
  height: 110px;
  background-repeat: no-repeat;
  background-image: url(${logo}), url(${background});
  background-position:
    center center,
    center center;
  background-size:
    auto 55px,
    cover;

  ${(props) =>
    props.$flex &&
    `
    @media(min-width: ${props.theme.collapse}px) {
      width: 240px;
      height: 148px;
      background-size: auto 43px, cover;
    }
  `}
`;
const StyledCard = styled.div`
  padding: 0;
  box-shadow: ${(props) => props.theme.cardShadow};
  border-radius: ${(props) => props.theme.borderRadius};
  overflow: hidden;
  color: ${(props) => props.theme.black700};
  font-size: 0.875rem;
  line-height: 1.6;

  @media (min-width: ${(props) => props.theme.collapse}px) {
    display: ${(props) => (props.$flex ? "flex" : "block")};
    font-size: ${(props) => (props.$flex ? "1rem" : "0.875rem")};
    align-items: center;
  }

  article {
    padding: 1rem;

    p {
      margin-bottom: 0.5rem;

      @media (min-width: ${(props) => props.theme.collapse}px) {
        margin-bottom: ${(props) => (props.$flex ? "1rem" : "0.5rem")};
      }
    }

    footer {
      display: flex;
      gap: 0.5rem;

      ${Button} {
        font-size: 0.813rem;
        font-weight: 600;
      }
    }
  }
`;

const TokTokCard = ({ flex = false, ...rest }) => (
  <StyledCard $flex={flex} {...rest}>
    <StyledLogo $flex={flex} aria-hidden="true" />
    <article>
      <p>Pour préparer vos porte-à-porte, utilisez la carte collaborative</p>
      <footer>
        <Button small link route="toktokPreview" color="primary">
          En savoir plus
        </Button>
        <Button small link route="toktok" icon="external-link" iconRight>
          Ouvrir la carte
        </Button>
      </footer>
    </article>
  </StyledCard>
);

export default TokTokCard;
