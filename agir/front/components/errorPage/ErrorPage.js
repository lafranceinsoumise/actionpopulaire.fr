import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { useAppLoader } from "@agir/front/app/hooks";

import Button from "@agir/front/genericComponents/Button";
import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import background from "@agir/front/genericComponents/images/illustration-404.svg";

const InterrogationMark = styled(RawFeatherIcon)`
  width: 3.5rem;
  height: 3.5rem;
  border-radius: 3.5rem;
  font-size: 2rem;
  background-color: ${(props) => props.theme.secondary500};
  display: inline-flex;
  justify-content: center;
  align-items: center;
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
  padding-top: 72px;

  h2 {
    text-align: center;
    font-size: 1.5rem;
  }

  pre {
    width: 100%;
    max-width: 750px;
    padding: 1.5rem;
    margin: 0 0 1rem;
    overflow: auto;
    background-color: ${(props) => props.theme.black50};
    border-radius: ${(props) => props.theme.borderRadius};
    text-align: center;
  }

  ${Button} {
    max-width: 450px;
  }
`;

const StyledPage = styled.div`
  display: flex;
  flex-direction: column;
  justify-content: center;
`;

export const ErrorPage = ({ errorMessage }) => {
  useAppLoader();
  return (
    <StyledPage>
      <StyledContainer>
        <InterrogationMark name="x" />
        <h2>Une erreur est survenue</h2>
        <span>Notre équipe a été prévenue du problème</span>
        <Spacer size="1rem" />
        {errorMessage && <pre>{errorMessage}</pre>}
        <Spacer size="1rem" />
        <Button link route="events" color="primary" block>
          Revenir à l'accueil
        </Button>
        <Spacer size="1rem" />
        <Button onClick={() => window.location.reload()} block>
          Recharger la page
        </Button>
        <Spacer size="1rem" />
        <span>
          ou consulter le <Link route="helpIndex">centre d'aide</Link>
        </span>
      </StyledContainer>
    </StyledPage>
  );
};
ErrorPage.propTypes = {
  errorMessage: PropTypes.string,
};
export default ErrorPage;
