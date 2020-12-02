import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { useGlobalContext } from "@agir/front/genericComponents/GlobalContext";

import Button from "@agir/front/genericComponents/Button";
import LogoAP from "@agir/front/genericComponents/LogoAP";

import footerBanner from "./images/footer-banner.png";

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

  & > div {
    display: flex;
    flex-flow: row nowrap;
    justify-content: space-between;
    align-items: center;
    line-height: 2rem;

    & > span {
      font-size: 14px;
    }

    & > ${Button} {
      color: ${style.black1000};
      font-size: 16px;
      font-weight: 700;
    }

    @media (max-width: ${style.collapse}px) {
      flex-flow: column nowrap;
      align-items: flex-start;

      & span {
        color: transparent;
        line-height: 0.5rem;
      }
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

const StyledFooter = styled.div`
  width: 100%;
  background-color: ${style.white};
  box-shadow: 0px 0px 3px rgba(0, 35, 44, 0.1),
    0px 2px 0px rgba(0, 35, 44, 0.08);

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
    padding: 60px 114px;

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

export const Footer = (props) => {
  const { isSignedIn, is2022, routes } = props;
  return (
    <footer>
      {isSignedIn === false ? (
        <FooterBanner>
          <h3>Agissez dans votre ville!</h3>
          {is2022 ? (
            <p>
              <strong>Action Populaire</strong> est la plate-forme d’action de
              la campagne de Jean-Luc Mélenchon pour 2022. Parrainez la
              candidature pour vous connecter :
            </p>
          ) : (
            <p>
              <strong>Action Populaire</strong> est la plate-forme d’action de
              la campagne de Jean-Luc Mélenchon pour 2022 et de la France
              insoumise. Inscrivez-vous d’une de ces façons :
            </p>
          )}
          <div>
            <Button
              as="a"
              color="secondary"
              href={routes.noussommespour && routes.noussommespour.home}
            >
              Parrainez la candidature
            </Button>
            <span>{!is2022 ? <>&nbsp;ou&nbsp;</> : <>&emsp;</>}</span>
            {is2022 ? (
              <Button as="a" color="white" href={routes.logIn}>
                J'ai déjà parrainé
              </Button>
            ) : (
              <Button
                as="a"
                color="white"
                href={routes.lafranceinsoumise && routes.lafranceinsoumise.home}
              >
                Rejoindre la France insoumise
              </Button>
            )}
          </div>
          <p>
            {is2022
              ? "Vous avez déjà un compte ? "
              : "Vous avez déjà rejoins la France Insoumise ? "}
            <a href={routes.logIn}>Je me connecte</a>
          </p>
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
              {isSignedIn
                ? routes.signOut && <a href={routes.signOut}>Se déconnecter</a>
                : routes.logIn && <a href={routes.logIn}>Se connecter</a>}
              {routes.donations && <a href={routes.donations}>Faire un don</a>}
              {routes.contact && <a href={routes.contact}>Contact</a>}
            </p>
          </div>
          {isSignedIn ? (
            <div>
              <h3>Explorer</h3>
              <p>
                {routes.eventMapPage && (
                  <a href={routes.events}>Evénements proches de chez moi</a>
                )}
                {routes.events && (
                  <a href={routes.eventMapPage}>Carte des évènements</a>
                )}
                {routes.groupMapPage && (
                  <a href={routes.groupMapPage}>Carte des groupes d’actions</a>
                )}
                {routes.thematicTeams && (
                  <a href={routes.thematicTeams}>Les livrets thématiques</a>
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
                      <a href={routes.noussommespour.home}>Signer</a>
                    )}
                    {routes.noussommespour.eventMapPage && (
                      <a href={routes.noussommespour.eventMapPage}>
                        Carte des évènements
                      </a>
                    )}
                    {routes.noussommespour.groupsMap && (
                      <a href={routes.noussommespour.groupsMap}>
                        Carte des groupes
                      </a>
                    )}
                  </p>
                </div>
              ) : null}
              {routes.lafranceinsoumise ? (
                <div>
                  <h3>La France insoumise</h3>
                  <p>
                    {routes.lafranceinsoumise.home && (
                      <a href={routes.lafranceinsoumise.home}>Rejoindre</a>
                    )}
                    {routes.lafranceinsoumise.eventMapPage && (
                      <a href={routes.lafranceinsoumise.eventMapPage}>
                        Carte des évènements
                      </a>
                    )}
                    {routes.lafranceinsoumise.groupsMap && (
                      <a href={routes.lafranceinsoumise.groupsMap}>
                        Carte des groupes d’actions
                      </a>
                    )}
                    {routes.lafranceinsoumise.thematicTeams && (
                      <a href={routes.lafranceinsoumise.thematicTeams}>
                        Les livrets thématiques
                      </a>
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
                <a href={routes.noussommespour.home}>Nous Sommes Pour !</a>
              )}
              {routes.lafranceinsoumise && (
                <a href={routes.lafranceinsoumise.home}>La France Insoumise</a>
              )}
              {routes.jlmBlog && (
                <a href={routes.jlmBlog}>Le blog de Jean-Luc Mélenchon</a>
              )}
              {routes.linsoumission && (
                <a href={routes.linsoumission}>L'insoumission</a>
              )}
            </p>
          </div>
        </article>
      </StyledFooter>
    </footer>
  );
};
Footer.propTypes = {
  isSignedIn: PropTypes.bool,
  is2022: PropTypes.bool,
  routes: PropTypes.object,
};
Footer.defaultProps = {
  isSignedIn: false,
  is2022: false,
};
const ConnectedFooter = () => {
  const { routes, user, is2022 } = useGlobalContext();
  return <Footer routes={routes} isSignedIn={!!user} is2022={is2022} />;
};
export default ConnectedFooter;
