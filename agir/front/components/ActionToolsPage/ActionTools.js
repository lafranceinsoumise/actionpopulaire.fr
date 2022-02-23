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
  box-shadow: ${(props) => props.theme.cardShadow};
  background-color: white;

  @media (max-width: ${(props) => props.theme.collapse}px) {
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
      color: ${(props) => props.theme.black700};
    }
  }
`;
const StyledCard = styled.ul`
  box-shadow: ${(props) => props.theme.cardShadow};
  border-radius: ${(props) => props.theme.borderRadius};
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
            background-color: ${(props) => props.theme.secondary500};
            color: ${(props) => props.theme.black1000};
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
            <Button small link route="publicMeeting">
              Organiser une réunion publique
            </Button>
          </span>
        </span>
      </StyledCardItem>
      <StyledCardItem route="coupDeFil">
        <i
          aria-hidden="true"
          css={`
            background-color: ${(props) => props.theme.green500};
            color: ${(props) => props.theme.white};
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
      <StyledCardItem route="createContact">
        <i
          aria-hidden="true"
          css={`
            background-color: ${(props) => props.theme.primary500};
            color: ${(props) => props.theme.white};
          `}
        >
          <RawFeatherIcon name="user-plus" />
        </i>
        <span>
          <strong>Ajouter un contact</strong>
          <span>
            Ajoutez un nouveau soutien à Mélenchon 2022 et à votre groupe
            d’action en quelques clics.
          </span>
        </span>
        <RawFeatherIcon aria-hidden="true" name="chevron-right" />
      </StyledCardItem>
      <StyledCardItem route="referralSearch">
        <i
          aria-hidden="true"
          css={`
            background-color: ${(props) => props.theme.referralPink};
            color: ${(props) => props.theme.white};
          `}
        >
          <RawFeatherIcon name="pen-tool" />
        </i>
        <span>
          <strong>Objectif : 500 parrainages</strong>
          <span>
            Soyez volontaire pour rencontrer des élu·es et obtenir leur
            signature.
          </span>
        </span>
        <RawFeatherIcon aria-hidden="true" name="chevron-right" />
      </StyledCardItem>
      <StyledCardItem route="materiel">
        <i
          aria-hidden="true"
          css={`
            background-color: ${(props) => props.theme.materielBlue};
            color: ${(props) => props.theme.white};
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
      <StyledCardItem route="votingProxyLandingPage">
        <i
          aria-hidden="true"
          css={`
            background-color: ${(props) => props.theme.votingProxyOrange};
            color: ${(props) => props.theme.white};
          `}
        >
          <RawFeatherIcon name="edit-3" />
        </i>
        <span>
          <strong>Se porter volontaire pour prendre une procuration</strong>
          <span>
            Inscrivez-vous comme volontaire et prenez une procuration de vote
            d’un·e citoyen·ne pour le 10 et 24 avril
          </span>
        </span>
        <RawFeatherIcon aria-hidden="true" name="chevron-right" />
      </StyledCardItem>
    </StyledCard>
  );
};

export default ActionTools;
