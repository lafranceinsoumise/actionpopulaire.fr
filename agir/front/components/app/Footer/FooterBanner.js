import React from "react";
import styled from "styled-components";

import Link from "@agir/front/app/Link";
import Button from "@agir/front/genericComponents/Button";

import footerBanner from "./images/footer-banner.jpg";

const FooterForm = styled.div`
  display: flex;
  flex-flow: column nowrap;
  align-items: flex-start;
  justify-content: center;
  color: ${(props) => props.theme.background0};
  padding: 0 10%;
  width: 100%;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    padding: 1.5rem;
  }

  & > * {
    color: inherit;
    max-width: 557px;
    margin: 0;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      max-width: 100%;
    }
  }

  & > * + * {
    margin-top: 1rem;
  }

  & > h3 {
    font-size: 1.875rem;
    font-weight: 800;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 1.25rem;
    }
  }

  & > div {
    display: flex;
    flex-flow: row nowrap;
    justify-content: space-between;
    align-items: center;
    line-height: 2rem;

    &.small-only {
      @media (min-width: ${(props) => props.theme.collapse}px) {
        display: none;
      }
    }

    &.large-only {
      @media (max-width: ${(props) => props.theme.collapse}px) {
        display: none;
      }
    }

    & > span {
      font-size: 14px;
      margin: 0 0.5rem;

      @media (max-width: ${(props) => props.theme.collapse}px) {
        margin: 0;
      }
    }

    & > ${Button} {
      color: ${(props) => props.theme.text1000};

      & + ${Button} {
        margin-left: 0.5rem;

        @media (max-width: ${(props) => props.theme.collapse}px) {
          margin-left: 0;
          margin-top: 0.5rem;
        }
      }
    }

    @media (max-width: ${(props) => props.theme.collapse}px) {
      flex-flow: column nowrap;
      align-items: flex-start;
    }
  }

  & > p {
    &:last-child {
      font-size: 14px;
    }

    a {
      color: inherit;
      text-decoration: underline;
      font-weight: 700;
    }
  }
`;
const StyledBanner = styled.div`
  width: calc(100% - 60px);
  max-width: 1400px;
  margin: 0 auto 1rem;
  background-color: ${(props) => props.theme.primary500};
  border-radius: ${(props) => props.theme.borderRadius};
  height: 360px;
  display: flex;
  flex-flow: row nowrap;
  align-items: stretch;
  overflow: hidden;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    width: 100%;
    border-radius: 0;
    height: auto;
    margin-bottom: 0;
  }

  ${FooterForm} {
    flex: 1 1 800px;
  }

  &::after {
    content: "";
    display: block;
    flex: 1 1 600px;
    background-repeat: no-repeat;
    background-size: cover;
    background-position: center center;
    background-image: url(${footerBanner});

    @media (max-width: ${(props) => props.theme.collapse}px) {
      display: none;
    }
  }
`;

export const FooterBanner = () => {
  return (
    <StyledBanner>
      <FooterForm>
        <h3>Agissez dans votre ville !</h3>
        <article>
          <p>
            <strong>Action Populaire</strong> est le réseau social d’action de
            la France insoumise.
          </p>
        </article>
        <div>
          <Button link color="secondary" route="signup">
            Créer mon compte
          </Button>
        </div>
        <p>
          Vous avez déjà un compte&nbsp;?
          <Link route="login">Je me connecte</Link>
        </p>
      </FooterForm>
    </StyledBanner>
  );
};

export default FooterBanner;
