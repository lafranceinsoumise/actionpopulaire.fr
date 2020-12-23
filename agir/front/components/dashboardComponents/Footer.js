import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getIs2022,
  getRoutes,
  getUser,
} from "@agir/front/globalContext/reducers";

import Link from "@agir/front/app/Link";
import Button from "@agir/front/genericComponents/Button";
import LogoAP from "@agir/front/genericComponents/LogoAP";

import footerBanner from "./images/footer-banner.png";

const FooterForm = styled.div`
  display: flex;
  flex-flow: column nowrap;
  align-items: flex-start;
  justify-content: center;
  color: ${style.white};
  padding: 0 144px;
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
    max-width: 1400px;
    margin: 0 auto;
    color: ${style.black1000};
    margin: 0 auto;
    display: flex;
    flex-flow: row nowrap;
    justify-content: flex-start;
    align-items: stretch;
    padding: 60px 0;

    @media (max-width: ${style.collapse}px) {
      flex-flow: column nowrap;
      width: 100%;
      padding: 1.5rem 1.5rem 100px;
    }

    & > div {
      flex: 0 0 auto;
      padding: 20px 40px;
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

const FooterWrapper = styled.footer`
  @media (max-width: ${style.collapse}px) {
    display: ${({ desktopOnly }) => (desktopOnly ? "none" : "block")};
  }
`;

export const Footer = (props) => {
  const { isSignedIn, is2022, routes, desktopOnly } = props;
  return (
    <FooterWrapper desktopOnly={desktopOnly}>
      {isSignedIn === false ? (
        <FooterBanner>
          <FooterForm>
            <h3>Agissez dans votre ville!</h3>
            <article>
              {is2022 ? (
                <p>
                  <strong>Action Populaire</strong> est la plateforme d’action
                  de la campagne de Jean-Luc Mélenchon pour 2022.
                </p>
              ) : (
                <p>
                  <strong>Action Populaire</strong> est la plateforme d’action
                  de la campagne de Jean-Luc Mélenchon pour 2022 et de la France
                  insoumise.
                </p>
              )}
              {is2022 ? (
                <p>Parrainez la candidature pour vous connecter :</p>
              ) : (
                <p>Inscrivez-vous d’une de ces façons :</p>
              )}
            </article>
            <div className="small-only">
              <Button
                as="a"
                color="secondary"
                small
                href={routes.noussommespour && routes.noussommespour.home}
              >
                Parrainer la candidature
              </Button>
              {!is2022 ? (
                <span style={{ overflowWrap: "normal" }}>&nbsp;ou&nbsp;</span>
              ) : null}
              {is2022 ? (
                <Button small as="a" color="white" href={routes.logIn}>
                  J'ai déjà parrainé
                </Button>
              ) : (
                <Button
                  as="a"
                  color="white"
                  small
                  href={
                    routes.lafranceinsoumise && routes.lafranceinsoumise.home
                  }
                >
                  Rejoindre la France insoumise
                </Button>
              )}
            </div>
            <div className="large-only">
              <Button
                as="a"
                color="secondary"
                href={routes.noussommespour && routes.noussommespour.home}
              >
                Parrainer la candidature
              </Button>
              {!is2022 ? <span>&nbsp;ou&nbsp;</span> : null}
              {is2022 ? (
                <Button as="a" color="white" href={routes.logIn}>
                  J'ai déjà parrainé
                </Button>
              ) : (
                <Button
                  as="a"
                  color="white"
                  href={
                    routes.lafranceinsoumise && routes.lafranceinsoumise.home
                  }
                >
                  Rejoindre la France insoumise
                </Button>
              )}
            </div>
            <p>
              {is2022
                ? "Vous avez déjà un compte ? "
                : "Vous avez déjà rejoint la France Insoumise ? "}
              <Link href={routes.logIn}>Je me connecte</Link>
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
              {!isSignedIn && routes.logIn && (
                <Link href={routes.logIn}>Se connecter</Link>
              )}
              {routes.donations && <Link route="donations">Faire un don</Link>}
              {routes.help && <Link route="help">Besoin d'aide ?</Link>}
              {routes.legal && <Link route="legal">Mentions légales</Link>}
              {routes.contact && <Link route="contact">Contact</Link>}
              {isSignedIn && routes.signOut && (
                <Link route="signOut">Se déconnecter</Link>
              )}
            </p>
          </div>
          {isSignedIn ? (
            <div>
              <h3>Explorer</h3>
              <p>
                {routes.events && (
                  <Link route="events">Evénements proches de chez moi</Link>
                )}
                {routes.eventMapPage && (
                  <Link route="eventMapPage">Carte des événements</Link>
                )}
                {routes.groupMapPage && (
                  <Link route="groupMapPage">Carte des groupes d’actions</Link>
                )}
                {routes.thematicTeams && (
                  <Link route="thematicTeams">Les livrets thématiques</Link>
                )}
              </p>
            </div>
          ) : (
            <>
              {routes.noussommespour ? (
                <div>
                  <h3>Nous sommes pour</h3>
                  <p>
                    {routes.noussommespour.home && (
                      <Link href={routes.noussommespour.home}>Signer</Link>
                    )}
                    {routes.noussommespour.eventMapPage && (
                      <Link href={routes.noussommespour.eventMapPage}>
                        Carte des événements
                      </Link>
                    )}
                    {routes.noussommespour.groupsMap && (
                      <Link href={routes.noussommespour.groupsMap}>
                        Carte des groupes
                      </Link>
                    )}
                  </p>
                </div>
              ) : null}
              {routes.lafranceinsoumise ? (
                <div>
                  <h3>La France insoumise</h3>
                  <p>
                    {routes.lafranceinsoumise.home && (
                      <Link href={routes.lafranceinsoumise.home}>
                        Rejoindre
                      </Link>
                    )}
                    {routes.lafranceinsoumise.eventMapPage && (
                      <Link href={routes.lafranceinsoumise.eventMapPage}>
                        Carte des événements
                      </Link>
                    )}
                    {routes.lafranceinsoumise.groupMapPage && (
                      <Link href={routes.lafranceinsoumise.groupMapPage}>
                        Carte des groupes d’actions
                      </Link>
                    )}
                    {routes.lafranceinsoumise.thematicTeams && (
                      <Link href={routes.lafranceinsoumise.thematicTeams}>
                        Les livrets thématiques
                      </Link>
                    )}
                  </p>
                </div>
              ) : null}
            </>
          )}
          <div>
            <h3>Les autres sites</h3>
            <p>
              {routes.noussommespour && (
                <Link href={routes.noussommespour.home}>
                  Nous Sommes Pour !
                </Link>
              )}
              {routes.lafranceinsoumise && (
                <Link href={routes.lafranceinsoumise.home}>
                  La France insoumise
                </Link>
              )}
              {routes.jlmBlog && (
                <Link href={routes.jlmBlog}>Le blog de Jean-Luc Mélenchon</Link>
              )}
              {routes.linsoumission && (
                <Link href={routes.linsoumission}>L'insoumission</Link>
              )}
            </p>
          </div>
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
};
Footer.defaultProps = {
  isSignedIn: false,
  is2022: false,
  desktopOnly: false,
};
const ConnectedFooter = (props) => {
  const is2022 = useSelector(getIs2022);
  const routes = useSelector(getRoutes);
  const user = useSelector(getUser);

  return (
    <Footer {...props} routes={routes} isSignedIn={!!user} is2022={is2022} />
  );
};
export default ConnectedFooter;
