import React from "react";
import styled, { useTheme } from "styled-components";

import Link from "@agir/front/app/Link";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

export const StyledIllustration = styled.div``;
export const StyledBody = styled.div``;

export const StyledMain = styled.main`
  margin: 0 auto;
  padding: 0 1.5rem;

  @media (min-width: ${(props) => props.theme.collapse}px) {
    max-width: 630px;
  }

  h2 {
    font-size: 1.375rem;
    font-weight: 700;
    margin: 0;
    line-height: 1.5;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 1.125rem;
    }
  }

  h5 {
    font-size: 1.125rem;
    font-weight: 600;
    margin: 0;
    line-height: 1.5;
    color: ${(props) => props.theme.primary500};
  }

  p {
    margin-bottom: 0;

    strong {
      font-weight: 600;
    }
  }

  ol {
    margin: 0;
    padding: 0;
    counter-reset: item;

    & > li {
      list-style-type: none;
      counter-increment: item;
      font-variant-numeric: tabular-nums;

      &:before {
        font-weight: 600;
        content: counter(item) ". ";
      }

      strong {
        font-weight: 600;
      }
    }
  }

  ul {
    max-width: 500px;
  }

  form {
    fieldset {
      margin: 0;
      padding: 0;
    }
  }

  a::not([type="button"]) {
    color: ${(props) => props.theme.primary500};

    &:hover,
    &:focus {
      color: ${(props) => props.theme.primary600};
    }
  }
`;

const Logo = (props) => {
  const theme = useTheme();

  return theme.Logo ? (
    <Link {...props}>
      <theme.Logo />
    </Link>
  ) : (
    <Link {...props} />
  );
};

export const StyledLogo = styled(Logo)`
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: ${(props) => props.theme.logoHeight};
  justify-items: stretch;
  width: calc(100% + 3rem);
  padding: 1rem 1.5rem;
  margin: -1rem -1.5rem 0;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    margin: 0 -1.5rem 1rem;
    padding: 1rem;
    border-bottom: 0.0625rem solid ${(props) => props.theme.text100};
  }

  &::before,
  svg {
    grid-column: 1/2;
    grid-row: 1/2;
    height: 100%;
    max-width: 100%;
  }

  &:empty::before {
    content: "";
    display: block;
    width: 100%;
    background-image: url(${(props) => props.theme.logo});
    background-repeat: no-repeat;
    background-position: center center;
    background-size: contain;
  }
`;

export const StyledPage = styled.div`
  @media (min-width: ${(props) => props.theme.collapse}px) {
    display: flex;
    width: 100vw;
    height: 100vh;
    overflow: hidden;
  }

  ${StyledIllustration} {
    flex: 0 0 623px;
    flex: 0 0 66.69921875vh;
    height: 100%;
    background-repeat: no-repeat;
    background-size: cover;
    background-position: center center;
    background-image: url(${(props) => props.theme.illustration.large});

    @media (max-width: ${(props) => props.theme.collapse}px) {
      content: url(${(props) => props.theme.illustration.small});
      width: 100%;
      height: auto;
    }
  }

  ${StyledBody} {
    padding: 0 0 80px;

    @media (min-width: ${(props) => props.theme.collapse}px) {
      flex: 1 1 auto;
      min-height: 100%;
      overflow: auto;
      padding: 80px 0;
    }
  }
`;

export const MailTo = () => (
  <div
    css={`
      padding: 0;
      color: ${({ theme }) => theme.text500};
      display: flex;
      align-items: start;
      gap: 1rem;

      & > :first-child {
        flex: 0 0 auto;
      }

      & > p {
        margin: 0;
        line-height: 1.5;

        & > a {
          font-weight: 600;
        }
      }
    `}
  >
    <FeatherIcon name="info" />
    <p
      css={`
        font-size: 0.875rem;

        a {
          color: ${({ theme }) => theme.primary500};

          &:hover,
          &:focus {
            color: ${({ theme }) => theme.primary600};
          }
        }
      `}
    >
      Besoin d'aide pour remplir le formulaire&nbsp;?{" "}
      <Link route="votingProxyHelp" target="_blank" rel="noopener noreferrer">
        Lisez notre tutoriel !
      </Link>
      <br />
      Une question&nbsp;? Écrivez-nous à l'adresse :{" "}
      <Link href="mailto:procurations@actionpopulaire.fr">
        procurations@actionpopulaire.fr
      </Link>
    </p>
  </div>
);

export const WarningBlock = styled(({ icon = "info", children, ...attrs }) => (
  <div {...attrs}>
    <FeatherIcon name={icon} />
    <p>{children}</p>
  </div>
))`
  padding: 1rem;
  background-color: ${({ theme, background }) => background || theme.primary50};
  display: flex;
  align-items: start;
  gap: 1rem;

  & > :first-child {
    flex: 0 0 auto;
    color: ${({ theme, iconColor }) => iconColor || theme.primary500};
  }

  & > p {
    margin: 0;
  }
`;

export const ElectoralInfoLink = () => (
  <WarningBlock>
    Vous pouvez trouver les informations demandées ci-dessous sur votre carte
    électorale ou sur{" "}
    <Link
      href="https://www.service-public.fr/particuliers/vosdroits/services-en-ligne-et-formulaires/ISE"
      target="_blank"
      rel="noopener noreferrer"
    >
      le site du service public
    </Link>
  </WarningBlock>
);
