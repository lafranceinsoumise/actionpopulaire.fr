/* eslint-disable react/no-unknown-property */
import React from "react";
import styled from "styled-components";

import Link from "@agir/front/app/Link";
import Button from "@agir/front/genericComponents/Button";
import FaIcon from "@agir/front/genericComponents/FaIcon";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { Hide } from "@agir/front/genericComponents/grid";

import vpIcon from "@agir/voting_proxies/Common/images/vp_icon.png";

const StyledCardItem = styled(Link)`
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: ${(props) => (props.$highlight ? 1.5 : 1)}rem;
  box-shadow: ${({ theme }) => theme.cardShadow};
  background-color: ${(props) =>
    props.$highlight ? props.theme[props.$highlight] : props.theme.white};

  @media (max-width: ${({ theme }) => theme.collapse}px) {
    align-items: flex-start;
    padding: 1.5rem 1rem;
  }

  &,
  &:hover,
  &:focus,
  &:active {
    text-decoration: none;
    color: inherit;
  }

  & > i {
    width: 3rem;
    height: 3rem;
    border-radius: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    line-height: 0;
    font-size: 0;
  }

  & > i,
  & > ${RawFeatherIcon}, & > ${Button}, & > img {
    flex: 0 0 auto;

    @media (max-width: 360px) {
      display: none;
    }
  }

  & > ${Button} {
    align-self: center;
  }

  & > span {
    flex: 1 1 auto;
    display: flex;
    flex-flow: column nowrap;
    gap: 0.25rem;

    & > strong {
      font-weight: ${(props) => (props.$highlight ? 700 : 500)};
      font-size: 1rem;
      line-height: 1.4;
    }

    & > span {
      font-size: 0.875rem;
      line-height: 1.5;
      color: ${({ theme }) => theme.black700};
    }
  }
`;
const StyledCard = styled.ul`
  box-shadow: ${({ theme }) => theme.cardShadow};
  border-radius: ${({ theme }) => theme.borderRadius};
  list-style-type: none;
  margin: 0;
  padding: 0;
  overflow: hidden;
`;

export const ActionTools = () => {
  return (
    <StyledCard>
      <StyledCardItem route="votingProxyLandingPage" $highlight="secondary100">
        <img width="58" height="53" src={vpIcon} />
        <span>
          <strong>Espace procurations</strong>
          <span>
            Absent·e le 9 juin ? Faites une procuration !
            <br />
            Disponible le 9 juin ? Prenez la procuration d'une personne absente
            pour voter !
          </span>
          <Hide
            $over
            as="span"
            css={`
              display: inline-flex;
              flex-wrap: wrap;
              gap: 0.5rem;
              margin-top: 0.25rem;
            `}
          >
            <Button small link route="donationLanding" color="primary">
              Faire un don
            </Button>
          </Hide>
        </span>
        <RawFeatherIcon aria-hidden="true" name="chevron-right" />
      </StyledCardItem>
      <StyledCardItem route="donationLanding" $highlight="primary50">
        <i
          aria-hidden="true"
          css={`
            background-color: #fd3d66;
            color: ${({ theme }) => theme.white};
          `}
        >
          <RawFeatherIcon name="heart" />
        </i>
        <span>
          <strong>Soutenir financièrement la France insoumise</strong>
          <span>
            Pour que le mouvement puisse financer ses frais de fonctionnement,
            organiser des actions et s’équiper en matériel, vous pouvez
            contribuer financièrement de manière ponctuelle ou mensuellement.
            Chaque euro compte.
          </span>
          <Hide
            $over
            as="span"
            css={`
              display: inline-flex;
              flex-wrap: wrap;
              gap: 0.5rem;
              margin-top: 0.25rem;
            `}
          >
            <Button small link route="donationLanding" color="primary">
              Faire un don
            </Button>
          </Hide>
        </span>
        <Hide $under as={Button} link route="donationLanding" color="primary">
          Faire un don
        </Hide>
      </StyledCardItem>
      <StyledCardItem as="span">
        <i
          aria-hidden="true"
          css={`
            background-color: ${({ theme }) => theme.primary500};
            color: ${({ theme }) => theme.white};
          `}
        >
          <RawFeatherIcon name="calendar" />
        </i>
        <span>
          <strong>Organiser une action</strong>
          <span>
            Porte-à-porte, tractage, caravane... Des fiches pratiques sont à
            votre disposition vour vous aider dans l'organisation de vos
            actions.
          </span>
          <span
            css={`
              display: inline-flex;
              flex-wrap: wrap;
              gap: 0.5rem;
              margin-top: 0.25rem;
            `}
          >
            <Button small link route="createEvent">
              Créer un événement
            </Button>
            <Button small link route="helpIndex">
              Voir les fiches pratiques
            </Button>
          </span>
        </span>
      </StyledCardItem>
      <StyledCardItem route="materiel">
        <i
          aria-hidden="true"
          css={`
            background-color: ${({ theme }) => theme.secondary500};
            color: ${({ theme }) => theme.black1000};
          `}
        >
          <RawFeatherIcon name="shopping-bag" />
        </i>
        <span>
          <strong>Commander du matériel</strong>
          <span>
            Commandez et recevez chez vous des tracts, des affiches et des
            objets des campagnes du mouvement.
          </span>
        </span>
        <RawFeatherIcon aria-hidden="true" name="chevron-right" />
      </StyledCardItem>
      {/*
        <StyledCardItem route="newPollingStationOfficer">
        <i
          aria-hidden="true"
          css={`
            background-color: ${({ theme }) => theme.referralPink};
            color: ${({ theme }) => theme.white};
          `}
        >
          <svg
            width="25"
            height="24"
            viewBox="0 0 25 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <g clipPath="url(#clip0_5242_40128)">
              <path
                d="M3.5 15H2C1.44772 15 1 15.4477 1 16V21C1 21.5523 1.44772 22 2 22H22C22.5523 22 23 21.5523 23 21V16.5C23 15.9477 22.5523 15.5 22 15.5H20.5M5.5 15.5V3C5.5 2.44772 5.94772 2 6.5 2H17.5C18.0523 2 18.5 2.44771 18.5 3V15.5C18.5 16.0523 18.0523 16.5 17.5 16.5H6.5C5.94772 16.5 5.5 16.0523 5.5 15.5Z"
                stroke="white"
                strokeWidth="2"
              />
              <path
                d="M9 8.6L10.299 10.1588C10.6754 10.6105 11.3585 10.6415 11.7743 10.2257L15 7"
                stroke="white"
                strokeWidth="2"
              />
            </g>
            <defs>
              <clipPath id="clip0_5242_40128">
                <rect
                  width="24"
                  height="24"
                  fill="white"
                  transform="translate(0.5)"
                />
              </clipPath>
            </defs>
          </svg>
        </i>
        <span>
          <strong>Devenir assesseur·e ou délégué·e</strong>
          <span>
            Pour la réussite de ce scrutin, soyons dans le plus grand nombre de
            bureaux de vote.
          </span>
        </span>
        <RawFeatherIcon aria-hidden="true" name="chevron-right" />
      </StyledCardItem>
      */}
      <StyledCardItem as="span">
        <i
          aria-hidden="true"
          css={`
            background-color: #00ace0;
            color: ${({ theme }) => theme.white};
          `}
        >
          <RawFeatherIcon name="radio" />
        </i>
        <span>
          <strong>Organiser une réunion publique</strong>
          <span>
            Demandez l'organisation d'une réunion publique, avec la présence
            d'un·e député·e ou eurodéputé·e.
          </span>
          <span
            css={`
              display: inline-flex;
              flex-wrap: wrap;
              gap: 0.5rem;
              margin-top: 0.25rem;
            `}
          >
            <Button small link route="publicMeetingRequest">
              Faire une demande de réunion publique
            </Button>
            <Button small link route="publicMeetingHelp">
              En savoir plus
            </Button>
          </span>
        </span>
      </StyledCardItem>
      <StyledCardItem route="cafePopulaireRequest">
        <i
          aria-hidden="true"
          css={`
            background-color: #00b171;
            color: ${({ theme }) => theme.white};
          `}
        >
          <RawFeatherIcon name="coffee" />
        </i>
        <span>
          <strong>Organiser un café populaire</strong>
          <span>
            Le café populaire est un exercice d’éducation populaire, de débat
            d’idées, et de formation politique mis en place par la France
            insoumise et organisé par l’Institut La Boétie, qui fournit un
            catalogue de thèmes et d'intervenant·es. Les cafés populaires
            peuvent être organisés partout en France et sont ouvert à tou·tes
            les citoyen·nes.
          </span>
          <span
            css={`
              display: inline-flex;
              flex-wrap: wrap;
              gap: 0.5rem;
              margin-top: 0.25rem;
            `}
          ></span>
        </span>
        <RawFeatherIcon aria-hidden="true" name="chevron-right" />
      </StyledCardItem>
      <StyledCardItem route="createContact">
        <i
          aria-hidden="true"
          css={`
            background-color: #4d26b9;
            color: ${({ theme }) => theme.white};
          `}
        >
          <RawFeatherIcon name="user-plus" />
        </i>
        <span>
          <strong>Ajouter un contact</strong>
          <span>
            Ajoutez un nouveau soutien à Action Populaire et à votre groupe
            d’action en quelques clics.
          </span>
        </span>
        <RawFeatherIcon aria-hidden="true" name="chevron-right" />
      </StyledCardItem>
      <StyledCardItem route="thematicGroups">
        <FaIcon
          icon="book-bookmark:regular"
          aria-hidden="true"
          css={`
            background-color: ${({ theme }) => theme.vermillon};
            color: ${({ theme }) => theme.white};
            && {
              font-size: 1.25em;
            }
          `}
        />
        <span>
          <strong>Rejoindre un groupe thématique</strong>
          <span>
            Les groupes thématiques de l'espace programme sont issus des travaux
            des livrets pendant la campagne présidentielle. Aujourd’hui, ces
            groupes continuent de produire du contenu, de réagir à l’actualité
            et de monter des initiatives.
          </span>
        </span>
        <RawFeatherIcon aria-hidden="true" name="chevron-right" />
      </StyledCardItem>
      <StyledCardItem as="span">
        <i
          aria-hidden="true"
          css={`
            background-color: ${({ theme }) => theme.PULBleu};
            color: ${({ theme }) => theme.white};
          `}
        >
          <svg
            width="24"
            height="24"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d="M19.5 21V1.5H4.5V21"
              stroke="white"
              strokeWidth="2.25"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <line
              x1="2.625"
              y1="21.375"
              x2="21.375"
              y2="21.375"
              stroke="white"
              strokeWidth="2.25"
              strokeLinecap="round"
              strokeLinejoin="round"
            />
            <circle cx="15" cy="10.5" r="1.5" fill="white" />
          </svg>
        </i>
        <span>
          <strong>TokTok - Carte du porte-à-porte</strong>
          <span>
            Ciblez les quartiers lorsque vous préparez vos actions grâce aux
            indications sur la carte et indiquez les portes auxquelles vous avez
            toqué
          </span>
          <span
            css={`
              display: inline-flex;
              flex-wrap: wrap;
              gap: 0.5rem;
              margin-top: 0.25rem;
            `}
          >
            <Button small link route="toktokPreview">
              En savoir plus
            </Button>
            <Button small link route="toktok" icon="external-link">
              Ouvrir la carte
            </Button>
          </span>
        </span>
      </StyledCardItem>
    </StyledCard>
  );
};

export default ActionTools;
