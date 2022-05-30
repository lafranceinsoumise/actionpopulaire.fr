import React from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledCardItem = styled(Link)`
  padding: 1.5rem;
  display: flex;
  align-items: center;
  gap: 1rem;
  box-shadow: ${({ theme }) => theme.cardShadow};
  background-color: white;

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
  & > ${RawFeatherIcon} {
    flex: 0 0 auto;

    @media (max-width: 360px) {
      display: none;
    }
  }

  & > span {
    flex: 1 1 auto;
    display: flex;
    flex-flow: column nowrap;
    gap: 0.25rem;

    & > strong {
      font-weight: 500;
      font-size: 1rem;
      line-height: 1.5;
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
      <StyledCardItem as="span">
        <i
          aria-hidden="true"
          css={`
            background-color: ${({ theme }) => theme.secondary500};
            color: ${({ theme }) => theme.black1000};
          `}
        >
          <RawFeatherIcon name="calendar" />
        </i>
        <span>
          <strong>Organiser une action</strong>
          <span>
            Porte-à-porte, tractage, caravane, réunion avec un·e orateur·ice de
            la campagne... Vous pouvez vous aider des{" "}
            <Link route="helpIndex">fiches pratiques</Link> pour organiser vos
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
          </span>
        </span>
      </StyledCardItem>
      <StyledCardItem route="newVotingProxy">
        <i
          aria-hidden="true"
          css={`
            background-color: ${({ theme }) => theme.votingProxyOrange};
            color: ${({ theme }) => theme.white};
          `}
        >
          <RawFeatherIcon name="edit-3" />
        </i>
        <span>
          <strong>Se porter volontaire pour prendre une procuration</strong>
          <span>
            Inscrivez-vous comme volontaire et prenez une procuration de vote
            d’un·e citoyen·ne pour le 12 et 19 juin
          </span>
        </span>
        <RawFeatherIcon aria-hidden="true" name="chevron-right" />
      </StyledCardItem>
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
      <StyledCardItem route="createContact">
        <i
          aria-hidden="true"
          css={`
            background-color: ${({ theme }) => theme.primary500};
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
            <Button small link route="toktok">
              Ouvrir la carte&ensp;{" "}
              <RawFeatherIcon
                width="0.813rem"
                height="0.813rem"
                name="external-link"
              />
            </Button>
          </span>
        </span>
      </StyledCardItem>
      <StyledCardItem route="coupDeFil">
        <i
          aria-hidden="true"
          css={`
            background-color: ${({ theme }) => theme.green500};
            color: ${({ theme }) => theme.white};
          `}
        >
          <RawFeatherIcon name="phone" />
        </i>
        <span>
          <strong>Coup de fil pour convaincre</strong>
          <span>
            Vous avez deux minutes&nbsp;? Appelez un·e citoyen·ne proche de chez
            vous pour le·a convaincre d’aller voter. On vous explique tout.
          </span>
        </span>
        <RawFeatherIcon aria-hidden="true" name="chevron-right" />
      </StyledCardItem>
      <StyledCardItem route="materiel">
        <i
          aria-hidden="true"
          css={`
            background-color: ${({ theme }) => theme.materielBlue};
            color: ${({ theme }) => theme.white};
          `}
        >
          <RawFeatherIcon name="shopping-bag" />
        </i>
        <span>
          <strong>Commander du matériel</strong>
          <span>
            Recevez chez vous des tracts, des affiches et des objets de la
            campagne.
          </span>
        </span>
        <RawFeatherIcon aria-hidden="true" name="chevron-right" />
      </StyledCardItem>
    </StyledCard>
  );
};

export default ActionTools;
