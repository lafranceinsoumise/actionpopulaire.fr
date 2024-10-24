import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Spacer from "@agir/front/genericComponents/Spacer";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import { WarningBlock } from "@agir/elections/Common/StyledComponents";
import Button from "@agir/front/genericComponents/Button";

const StyledList = styled.ul`
  list-style-type: none;
  padding: 0;

  li {
    display: flex;
    align-items: start;
    gap: 1rem;

    & > :first-child {
      flex: 0 0 auto;
      color: ${(props) => props.theme.primary500};
    }
  }
`;
const StyledWarningBlock = styled(WarningBlock)`
  & > p {
    display: flex;
    flex-flow: column nowrap;
    align-items: start;
    gap: 1rem;
    font-size: 0.875rem;

    ${Button} {
      flex: 0 0 auto;
      margin-left: auto;
    }
  }
`;

const NewVotingProxyHowTo = ({ user }) => (
  <div>
    {!!user && user?.votingProxyId && (
      <>
        <StyledWarningBlock icon="alert-circle">
          <span>
            Une inscription liée à votre compte Action populaire{" "}
            <strong>{user.email}</strong> existe déjà. Vous pouvez{" "}
            {user.hasVotingProxyRequests
              ? "consulter les procurations que vous avez acceptées"
              : "voir si des demandes sont en attente près de chez vous"}{" "}
            à l'aide du bouton ci-dessous.
          </span>
          {user.hasVotingProxyRequests ? (
            <Button
              link
              small
              color="primary"
              route="acceptedVotingProxyRequests"
              routeParams={{ votingProxyPk: user.votingProxyId }}
            >
              Voir mes procurations en cours
            </Button>
          ) : (
            <Button
              link
              small
              color="primary"
              route="votingProxyRequestsForProxy"
              routeParams={{ votingProxyPk: user.votingProxyId }}
            >
              Voir les demandes en attente
            </Button>
          )}
        </StyledWarningBlock>
        <Spacer size="1rem" />
      </>
    )}
    <h2>Se porter volontaire pour prendre une procuration</h2>
    <Spacer size="1rem" />
    <p>
      Vous êtes disponible les dimanches 30 juin et/ou 7 juillets, jours de vote
      pour les élections léglislatives, et vous souhaitez prendre la procuration
      d'une personne absente pour voter. Merci pour votre aide !
    </p>
    <Spacer size="1rem" />
    <StyledList>
      <li>
        <FeatherIcon name="arrow-right" />
        <span>
          <strong>Remplissez ce formulaire</strong> en indiquant vos coordonnées
        </span>
      </li>
      <Spacer size="0.5rem" />
      <li>
        <FeatherIcon name="arrow-right" />
        <span>
          <strong>Vous recevrez un SMS à valider</strong> quand une personne
          proche de chez vous souhaitera faire une procuration.
        </span>
      </li>
      <Spacer size="0.5rem" />
      <li>
        <FeatherIcon name="arrow-right" />
        <span>
          <strong>Vous allez voter en son nom</strong> le jour du scrutin dans
          son bureau de vote
        </span>
      </li>
    </StyledList>
    <Spacer size="1rem" />
    <p
      css={`
        line-height: 1.5;
        padding: 1rem;
        background-color: ${({ theme }) => theme.primary50};
        border-radius: ${({ theme }) => theme.borderRadius};
      `}
    >
      Depuis le 1er janvier 2022,{" "}
      <strong>
        il est possible de voter pour une personne inscrite sur les listes
        électorales d'une autre commune.
      </strong>{" "}
      Ainsi, si vous votez dans la commune A, vous pourrez voter pour un·e
      électeur·rice qui est inscrit·e dans la commune B. Cependant,{" "}
      <strong>vous devrez vous rendre dans son bureau de vote</strong> pour
      voter à sa place le jour du scrutin.
      <br />
      <br />
      Si vous êtes en déplacement, vous pourrez prendre une procuration là où
      vous vous trouvez, et cela même si quelqu'un vote pour vous par
      procuration dans votre commune.
    </p>
  </div>
);

NewVotingProxyHowTo.propTypes = {
  user: PropTypes.shape({
    votingProxyId: PropTypes.string,
    hasVotingProxyRequests: PropTypes.bool,
  }),
};

export default NewVotingProxyHowTo;
