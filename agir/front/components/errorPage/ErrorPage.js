import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { useAppLoader } from "@agir/front/app/hooks";

import Button from "@agir/front/genericComponents/Button";
import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";
import TopBar from "@agir/front/app/Navigation/TopBar";

import background from "@agir/front/genericComponents/images/illustration-404.svg";

const StyledIcon = styled.div`
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 3.5rem;
  font-size: 2rem;
  background-color: ${(props) => props.theme.secondary500};
  display: inline-flex;
  justify-content: center;
  align-items: center;
  font-weight: 500;
`;

const StyledContainer = styled.div`
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 100%;
  min-height: 100vh;
  position: relative;
  overflow: auto;
  background-image: url("${background}");
  background-position: center;
  background-size: cover;
  background-repeat: no-repeat;
  padding: 1.5rem 1rem;

  h2 {
    text-align: center;
    font-size: 1.5rem;
  }

  p {
    width: 100%;
    max-width: 46.875rem;
    text-align: center;
  }

  pre {
    width: 100%;
    max-width: 46.875rem;
    padding: 1.5rem;
    margin: 0 0 1rem;
    overflow: auto;
    background-color: ${(props) => props.theme.text50};
    border-radius: ${(props) => props.theme.borderRadius};
    text-align: center;
  }

  ${Button} {
    max-width: 28.125rem;
  }
`;

const StyledPage = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
`;

export const ErrorPage = (props) => {
  const {
    title = "Une erreur est survenue",
    subtitle = "Notre équipe a été prévenue du problème",
    errorMessage,
    hasReload = true,
    hasTopBar = true,
    icon,
    children,
  } = props;

  useAppLoader();

  return (
    <StyledPage>
      {hasTopBar && (
        <>
          <TopBar hasTopBar />
          <Spacer size="4.625rem" />
        </>
      )}
      {children ? (
        <StyledContainer>{children}</StyledContainer>
      ) : (
        <StyledContainer>
          <StyledIcon>{icon || <RawFeatherIcon name="x" />}</StyledIcon>
          <h2>{title}</h2>
          <p>{subtitle}</p>
          <Spacer size="1rem" />
          {errorMessage && <pre>{errorMessage}</pre>}
          <Spacer size="1rem" />
          <Button link route="events" color="primary" block>
            Revenir à l'accueil
          </Button>
          {hasReload ? (
            <>
              <Spacer size="1rem" />
              <Button onClick={() => window.location.reload()} block>
                Recharger la page
              </Button>
            </>
          ) : null}
          <Spacer size="1rem" />
          <span>
            ou consulter le <Link route="helpIndex">centre d'aide</Link>
          </span>
        </StyledContainer>
      )}
    </StyledPage>
  );
};
ErrorPage.propTypes = {
  errorMessage: PropTypes.string,
  title: PropTypes.string,
  subtitle: PropTypes.string,
  hasReload: PropTypes.bool,
  hasTopBar: PropTypes.bool,
  icon: PropTypes.node,
  children: PropTypes.node,
};
export default ErrorPage;
