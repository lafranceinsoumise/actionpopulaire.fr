import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { useGlobalContext } from "@agir/front/genericComponents/GlobalContext";

import Button from "@agir/front/genericComponents/Button";

import footerBanner from "./images/footer-banner.png";
import googlePlayBadge from "./images/google-play-badge.png";
import appStoreBadge from "./images/app-store-badge.svg";

const FooterBanner = styled.div`
  position: relative;
  top: 40px;
  width: calc(100% - 60px);
  max-width: 1400px;
  margin: 0 auto;
  background-color: ${style.primary500};
  border-radius: 8px;
  height: 360px;
  display: flex;
  flex-flow: column nowrap;
  align-items: flex-start;
  justify-content: center;
  color: ${style.white};
  padding: 0 144px;
  background-repeat: no-repeat;
  background-size: auto 100%;
  background-position: top right;
  background-image: url(${footerBanner});

  @media (max-width: ${style.collapse}px) {
    position: static;
    width: 100%;
    background-image: none;
    border-radius: 0;
    padding: 0 1.5rem;
    height: 328px;
  }

  & > * {
    color: inherit;
    max-width: 557px;
    margin: 0;
  }

  & > * + * {
    margin-top: 1rem;
  }

  & > h3 {
    font-size: 30px;
    font-weight: 800;
  }

  & > ${Button} {
    background-color: ${style.white};
    color: ${style.primary500};
    font-size: 16px;
    font-weight: 700;
  }

  & > p {
    :last-child {
      font-size: 14px;
    }

    a {
      color: inherit;
      text-decoration: underline;
      font-weight: 700;
    }
  }
`;

const StyledFooter = styled.div`
  width: 100%;
  background-color: ${style.black1000};

  article {
    width: 100%;
    max-width: 1400px;
    margin: 0 auto;
    color: ${style.white};
    margin: 0 auto;
    display: flex;
    flex-flow: row nowrap;
    justify-content: flex-start;
    align-items: stretch;
    padding: 60px 114px;

    @media (max-width: ${style.collapse}px) {
      flex-flow: column nowrap;
      width: 100%;
      padding: 1.5rem 1.5rem 114px;
    }

    & > div {
      flex: 0 0 auto;
      padding: 20px;
      color: inherit;

      &:first-child {
        @media (max-width: ${style.collapse}px) {
          display: none;
        }
      }

      &:last-child {
        margin-left: auto;

        @media (max-width: ${style.collapse}px) {
          display: flex;
          flex-flow: row nowrap;
          justify-content: flex-start;
          width: 100%;
        }

        a {
          display: block;
          width: 153px;
          height: 45px;
          margin-bottom: 0.75rem;
          font-size: 0;
          background-repeat: no-repeat;
          background-size: cover;
          background-position: center center;
          border: 1px solid white;
          border-radius: 8px;

          @media (max-width: ${style.collapse}px) {
            margin-bottom: 0;
            margin-right: 0.75rem;
          }

          :nth-child(1) {
            background-image: url(${googlePlayBadge});
            background-size: 115%;
          }

          :nth-child(2) {
            background-image: url(${appStoreBadge});
          }
        }
      }

      img {
        width: 125px;
        height: 62px;
        background-color: ${style.white};
      }

      h3 {
        color: inherit;
        text-transform: uppercase;
        margin-top: 0;
        margin-bottom: 0.75rem;
        font-size: 12px;
        font-weight: bold;
      }

      p {
        color: inherit;
        font-weight: 400;
        font-size: 13px;

        a {
          display: block;
          color: inherit;
          margin-bottom: 0.75rem;
        }
      }
    }
  }
`;

export const Footer = (props) => {
  const { isSignedIn } = props;
  return (
    <footer>
      {isSignedIn === false ? (
        <FooterBanner>
          <h3>Agissez dans votre ville!</h3>
          <p>
            <strong>Action Populaire</strong> est la plate-forme d’action
            communautaire de la France Insoumise et des mouvements soutenants la
            candidature de Jean-Luc Mélenchon pour 2022.
          </p>
          <Button as="a" href="#">
            Je crée mon compte
          </Button>
          <p>
            Vous avez déjà un compte ? <a href="#">Je me connecte</a>
          </p>
        </FooterBanner>
      ) : null}
      <StyledFooter>
        <article>
          <div>
            <img />
          </div>
          <div>
            <h3>Action populaire</h3>
            <p>
              <a href="#">Créer un compte</a>
              <a href="#">Se connecter</a>
              <a href="#">Contact</a>
            </p>
          </div>
          <div>
            <h3>Explorer</h3>
            <p>
              <a href="#">Evénements proches de chez moi</a>
              <a href="#">Carte des évènements</a>
              <a href="#">Carte des groupes d’actions</a>
              <a href="#">Les livrets thématiques</a>
            </p>
          </div>
          <div>
            <h3>Les autres sites</h3>
            <p>
              <a href="#">Nous Sommes Pour !</a>
              <a href="#">La France Insoumise</a>
            </p>
          </div>
          <div>
            <a href="#">Play store</a>
            <a href="#">Apple store</a>
          </div>
        </article>
      </StyledFooter>
    </footer>
  );
};
Footer.propTypes = {
  isSignedIn: PropTypes.bool,
  routes: PropTypes.object,
};
Footer.defaultProps = {
  isSignedIn: false,
};
const ConnectedFooter = () => {
  const { routes, user } = useGlobalContext();
  return <Footer routes={routes} isSignedIn={!!user} />;
};
export default ConnectedFooter;
