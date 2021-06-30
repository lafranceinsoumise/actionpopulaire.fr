import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getIs2022,
  getIsSessionLoaded,
  getRoutes,
  getUser,
} from "@agir/front/globalContext/reducers";

import AppStore from "@agir/front/genericComponents/AppStore";
import Link from "@agir/front/app/Link";
import Button from "@agir/front/genericComponents/Button";
import LogoAP from "@agir/front/genericComponents/LogoAP";
import Spacer from "@agir/front/genericComponents/Spacer";

import footerBanner from "./images/footer-banner.jpg";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";
import { useMobileApp } from "@agir/front/app/hooks";
import { routeConfig } from "@agir/front/app/routes.config";

const FooterForm = styled.div`
  display: flex;
  flex-flow: column nowrap;
  align-items: flex-start;
  justify-content: center;
  color: ${style.white};
  padding: 0 10%;
  width: 100%;

  @media (max-width: ${style.collapse}px) {
    padding: 1.5rem;
  }

  & > * {
    color: inherit;
    max-width: 557px;
    margin: 0;

    @media (max-width: ${style.collapse}px) {
      max-width: 100%;
    }
  }

  & > * + * {
    margin-top: 1rem;
  }

  & > h3 {
    font-size: 1.875rem;
    font-weight: 800;

    @media (max-width: ${style.collapse}px) {
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
      @media (min-width: ${style.collapse}px) {
        display: none;
      }
    }

    &.large-only {
      @media (max-width: ${style.collapse}px) {
        display: none;
      }
    }

    & > span {
      font-size: 14px;
      margin: 0 0.5rem;

      @media (max-width: ${style.collapse}px) {
        margin: 0;
      }
    }

    & > ${Button} {
      color: ${style.black1000};

      & + ${Button} {
        margin-left: 0.5rem;

        @media (max-width: ${style.collapse}px) {
          margin-left: 0;
          margin-top: 0.5rem;
        }
      }
    }

    @media (max-width: ${style.collapse}px) {
      flex-flow: column nowrap;
      align-items: flex-start;
    }
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
const FooterBanner = styled.div`
  width: calc(100% - 60px);
  max-width: 1400px;
  margin: 0 auto 1rem;
  background-color: ${style.primary500};
  border-radius: 8px;
  height: 360px;
  display: flex;
  flex-flow: row nowrap;
  align-items: stretch;
  overflow: hidden;

  @media (max-width: ${style.collapse}px) {
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

    @media (max-width: ${style.collapse}px) {
      display: none;
    }
  }
`;

const StyledFooter = styled.div`
  width: 100%;
  background-color: ${style.white};
  border-top: 1px solid ${style.black100};

  article {
    width: 100%;
    max-width: 1200px;
    margin: 0 auto;
    color: ${style.black1000};
    margin: 0 auto;
    display: flex;
    flex-flow: row nowrap;
    justify-content: space-around;
    align-items: stretch;
    padding: 60px 0;

    @media (max-width: ${style.collapse}px) {
      flex-flow: column nowrap;
      width: 100%;
      padding: 1.5rem 1.5rem 0;
    }

    & > div {
      flex: 0 0 auto;
      padding: 20px 0;
      color: inherit;

      @media (max-width: ${style.collapse}px) {
        padding: 20px 0;

        &:first-child {
          display: none;
        }
      }

      img {
        width: 125px;
        height: 62px;
        background-color: ${style.white};
      }

      h3 {
        color: ${style.primary500};
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

const FooterWrapper = styled.footer`
  @media (max-width: ${style.collapse}px) {
    display: ${({ desktopOnly }) => (desktopOnly ? "none" : "block")};
    padding-bottom: 72px;
  }
`;

export const Footer = (props) => {
  const {
    hideBanner,
    isSignedIn,
    is2022,
    routes,
    desktopOnly,
    displayOnMobileApp,
  } = props;

  const { isMobileApp } = useMobileApp();
  const hasBanner = !hideBanner && isSignedIn === false;

  if (isMobileApp && !displayOnMobileApp) return null;

  return (
    <FooterWrapper desktopOnly={desktopOnly}>
      {hasBanner ? (
        <FooterBanner>
          <FooterForm>
            <h3>Agissez dans votre ville!</h3>
            <article>
              {is2022 ? (
                <p>
                  <strong>Action Populaire</strong> est le réseau social
                  d’action de la campagne de Jean-Luc Mélenchon pour 2022.
                </p>
              ) : (
                <p>
                  <strong>Action Populaire</strong> est le réseau social
                  d’action de la campagne de Jean-Luc Mélenchon pour 2022 et de
                  la France insoumise.
                </p>
              )}
            </article>
            <div>
              <Button as="Link" color="secondary" route="signup">
                Créer mon compte
              </Button>
            </div>
            <p>
              Vous avez déjà un compte&nbsp;?
              <Link route="login">Je me connecte</Link>
            </p>
          </FooterForm>
        </FooterBanner>
      ) : null}
      <StyledFooter>
        <article>
          <div>
            <LogoAP />
          </div>
          <div>
            <h3>Action populaire</h3>
            <p>
              {routes.donations && <Link route="donations">Faire un don</Link>}
              <Link route="eventMap">Carte des événements</Link>
              <Link route="groupMap">Carte des groupes</Link>
              <a href="https://materiel.lafranceinsoumise.fr/" target="_blank">
                Commander du matériel
              </a>
            </p>
          </div>

          <div>
            <h3>Liens utiles</h3>
            <p>
              {!isSignedIn && <Link route="login">Se connecter</Link>}
              {isSignedIn && <Link route="logout">Se déconnecter</Link>}
              {routes.help && <Link route="help">Besoin d'aide ?</Link>}
              {routes.legal && <Link route="legal">Mentions légales</Link>}
              {routes.contact && <Link route="contact">Contact</Link>}
            </p>
          </div>

          <div>
            <h3>La campagne présidentielle</h3>
            <p>
              <a href="https://melenchon2022.fr/" target="_blank">
                Mélenchon2022.fr
              </a>
              {routes.programme && (
                <Link
                  href="https://melenchon2022.fr/programme/"
                  target="_blank"
                >
                  Le programme l'Avenir en commun
                </Link>
              )}
              <a href="https://melenchon2022.fr/agenda/" target="_blank">
                Agenda de la campagne
              </a>
            </p>
          </div>

          <div>
            <h3>Les autres sites</h3>
            <p>
              {routes.lafranceinsoumise && (
                <Link href={routes.lafranceinsoumise.home}>
                  La France insoumise
                </Link>
              )}

              {routes.linsoumission && (
                <Link href={routes.linsoumission}>L'insoumission</Link>
              )}
              {routes.jlmBlog && (
                <Link href={routes.jlmBlog}>Le blog de Jean-Luc Mélenchon</Link>
              )}
            </p>
          </div>

          {!isMobileApp && (
            <div>
              <AppStore type="apple" />
              <Spacer size="10px" />
              <AppStore type="google" />
            </div>
          )}
        </article>
      </StyledFooter>
    </FooterWrapper>
  );
};
Footer.propTypes = {
  isSignedIn: PropTypes.bool,
  is2022: PropTypes.bool,
  routes: PropTypes.object,
  desktopOnly: PropTypes.bool,
  hideBanner: PropTypes.bool,
  displayOnMobileApp: PropTypes.bool,
};
Footer.defaultProps = {
  isSignedIn: false,
  is2022: false,
  desktopOnly: false,
  hideBanner: false,
  displayOnMobileApp: false,
};
const ConnectedFooter = (props) => {
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const is2022 = useSelector(getIs2022);
  const routes = useSelector(getRoutes);
  const user = useSelector(getUser);

  return (
    <PageFadeIn ready={isSessionLoaded}>
      <Footer {...props} routes={routes} isSignedIn={!!user} is2022={is2022} />
    </PageFadeIn>
  );
};
export default ConnectedFooter;
