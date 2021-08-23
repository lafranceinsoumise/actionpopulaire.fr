import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Button from "@agir/front/genericComponents/Button";
import Link from "@agir/front/app/Link";
import Spacer from "@agir/front/genericComponents/Spacer";
import TopBar from "@agir/front/allPages/TopBar/TopBar";

const StyledWrapper = styled.main`
  margin: 0 auto;
  text-align: center;
  padding-top: 172px;
  padding-bottom: 2rem;

  @media (max-width: ${style.collapse}px) {
    padding-top: 100px;
  }

  & > * {
    margin: 0;
  }

  h2 {
    font-size: 1.625rem;
    line-height: 1.5;
    font-weight: 700;
  }
`;

const AuthenticatedLogin = ({ user }) => {
  return (
    <>
      <TopBar />
      <StyledWrapper>
        <h2>Vous êtes déjà connecté</h2>
        <Spacer size="1rem" />
        <p>
          Vous êtes déjà connecté·e à votre
          <br />
          compte <strong>{user.email}</strong>
        </p>
        <Spacer size="2rem" />
        <Button link route="dashboard" color="secondary">
          Revenir à l’accueil
        </Button>
        <Spacer size="3.25rem" />
        <p>
          Mauvais compte&nbsp;? <Link route="logout">Se déconnecter</Link>
        </p>
      </StyledWrapper>
    </>
  );
};
AuthenticatedLogin.propTypes = {
  user: PropTypes.oneOfType([
    PropTypes.shape({
      email: PropTypes.string.isRequired,
    }),
    PropTypes.bool,
  ]),
};
export default AuthenticatedLogin;
