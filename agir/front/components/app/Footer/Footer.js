import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

import AppStore from "@agir/front/genericComponents/AppStore";
import Link from "@agir/front/app/Link";
import LogoAP from "@agir/front/genericComponents/LogoAP";
import Spacer from "@agir/front/genericComponents/Spacer";

import FooterBanner from "./FooterBanner";

const StyledAppStore = styled(AppStore)``;
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
    padding: 60px 1.5rem;
    gap: 1rem;

    @media (max-width: ${style.collapse}px) {
      flex-flow: column nowrap;
      width: 100%;
      padding: 1.5rem 1.5rem 0;
    }

    & > div {
      padding: 20px 0;
      color: inherit;

      @media (min-width: ${style.collapse}px) {
        flex: 0 1 auto;
        min-width: 110px;

        &:first-child {
          min-width: 0;
          flex: 0 0 auto;
        }

        &:last-child {
          min-width: 0;
          flex-basis: 170px;

          ${StyledAppStore} {
            width: 100%;
            background-size: contain;
            background-position: top center;
          }
        }
      }

      @media (max-width: ${style.collapse}px) {
        flex: 0 0 auto;

        &:first-child {
          display: none;
        }
      }

      img {
        width: 100%;
        height: auto;

        @media (max-width: ${style.collapse}px) {
          width: 125px;
          height: 62px;
        }
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
    padding-bottom: 72px;
  }
`;

export const Footer = (props) => {
  const { isSignedIn, hasBanner, isMobileApp } = props;

  return (
    <FooterWrapper>
      {hasBanner && <FooterBanner />}
      <StyledFooter>
        <article>
          <div>
            <LogoAP />
          </div>
          <div>
            <h3>Action populaire</h3>
            <p>
              <Link route="donationLanding">Faire un don</Link>
              <Link route="eventMap">Carte des événements</Link>
              <Link route="groupMap">Carte des groupes</Link>
              <Link route="materiel" target="_blank">
                Commander du matériel
              </Link>
            </p>
          </div>

          <div>
            <h3>Liens utiles</h3>
            <p>
              {isSignedIn ? (
                <Link route="logout">Se déconnecter</Link>
              ) : (
                <Link route="login">Se connecter</Link>
              )}
              <Link route="help">Besoin d'aide&nbsp;?</Link>
              <Link route="legal">Mentions légales</Link>
              <Link route="contact">Contact</Link>
            </p>
          </div>

          <div>
            <h3>Le programme</h3>
            <p>
              <Link route="programme">Le site du programme</Link>
              <Link route="thematicGroups">Les groupes thématiques</Link>
              <Link route="avenir-en-commun" target="_blank">
                Le programme l'Avenir en commun
              </Link>
              <Link route="nupesPlatform" target="_blank">
                Le programme de la{" "}
                <abbr title="Nouvelle Union Populaire Écologique et sociale">
                  NUPES
                </abbr>
              </Link>
            </p>
          </div>

          <div>
            <h3>Les autres sites</h3>
            <p>
              <Link route="lafranceinsoumise">La France insoumise</Link>
              <Link route="linsoumission">L'insoumission</Link>
              <Link route="jlmBlog">Le blog de Jean-Luc Mélenchon</Link>
              <Link route="nupes" target="_blank">
                La{" "}
                <abbr title="Nouvelle Union Populaire Écologique et sociale">
                  NUPES
                </abbr>
              </Link>
            </p>
          </div>

          {!isMobileApp && (
            <div>
              <StyledAppStore type="apple" />
              <Spacer size="10px" />
              <StyledAppStore type="google" />
            </div>
          )}
        </article>
      </StyledFooter>
    </FooterWrapper>
  );
};
Footer.propTypes = {
  isSignedIn: PropTypes.bool,
  hasBanner: PropTypes.bool,
  isMobileApp: PropTypes.bool,
};

export default Footer;
