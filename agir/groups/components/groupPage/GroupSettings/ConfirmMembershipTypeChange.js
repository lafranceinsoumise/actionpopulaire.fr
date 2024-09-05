import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import BackButton from "@agir/front/genericComponents/ObjectManagement/BackButton";
import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";

import { MEMBERSHIP_TYPES } from "@agir/groups/utils/group";
import { getGenderedWord } from "@agir/lib/utils/display";

const StyledContent = styled.div`
  p {
    color: ${(props) => props.theme.text700};
    font-size: 1rem;
  }
`;
const StyledFooter = styled.footer`
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  grid-gap: 1rem;

  ${Button} {
    margin: 0;
    ${"" /* TODO: remove after Button refactoring merge */}
    justify-content: center;
    border-radius: ${(props) => props.theme.borderRadius};
  }
`;

const ConfirmPanel = (props) => {
  const {
    onBack,
    onConfirm,
    selectedMember,
    selectedMembershipType,
    isLoading,
  } = props;

  if (!selectedMember) {
    return null;
  }

  if (
    selectedMember.membershipType === MEMBERSHIP_TYPES.MEMBER &&
    selectedMembershipType === MEMBERSHIP_TYPES.FOLLOWER
  ) {
    return (
      <>
        <BackButton disabled={isLoading} onClick={onBack} />
        <StyledTitle>
          Retirer {selectedMember.displayName} des membres actifs&nbsp;?
        </StyledTitle>
        <Spacer size="0.5rem" />
        <StyledContent>
          <p>
            Cette personne ne sera plus considérée comme un membre actif de
            votre groupe.
          </p>
          <p>
            {getGenderedWord(selectedMember.gender, "Ce membre", "Elle", "Il")}{" "}
            ne recevra plus les messages postés sur Action Populaire que vous
            destinez aux membres actifs.
          </p>
          <p>
            {selectedMember.displayName} restera parmi les contacts de votre
            groupe.
          </p>
        </StyledContent>
        <Spacer size="1rem" />
        <StyledFooter>
          <Button disabled={isLoading} color="danger" onClick={onConfirm}>
            Retirer
          </Button>
          <Button disabled={isLoading} onClick={onBack}>
            Annuler
          </Button>
        </StyledFooter>
      </>
    );
  }

  if (
    selectedMember.membershipType === MEMBERSHIP_TYPES.FOLLOWER &&
    selectedMembershipType === MEMBERSHIP_TYPES.MEMBER
  ) {
    return (
      <>
        <BackButton disabled={isLoading} onClick={onBack} />
        <StyledTitle>
          Passer {selectedMember.displayName} en membre actif&nbsp;?
        </StyledTitle>
        <Spacer size="0.5rem" />
        <StyledContent>
          <p>
            Ce membre pourra accéder aux messages du groupe destinés aux membres
            actifs.
          </p>
        </StyledContent>
        <Spacer size="1rem" />
        <StyledFooter>
          <Button disabled={isLoading} color="primary" onClick={onConfirm}>
            Passer en membre actif
          </Button>
          <Button disabled={isLoading} onClick={onBack}>
            Annuler
          </Button>
        </StyledFooter>
      </>
    );
  }

  if (
    selectedMember.membershipType === MEMBERSHIP_TYPES.MEMBER &&
    selectedMembershipType === MEMBERSHIP_TYPES.MANAGER
  ) {
    return (
      <>
        <BackButton disabled={isLoading} onClick={onBack} />
        <StyledTitle>
          Passer {selectedMember.displayName} en gestionnaire&nbsp;?
        </StyledTitle>
        <Spacer size="0.5rem" />
        <StyledContent>
          <p>
            Ce membre pourra avoir accès à la liste et aux informations des
            membres du groupe, modifier les informations du groupe et créer des
            événements au nom du groupe
          </p>
        </StyledContent>
        <Spacer size="1rem" />
        <StyledFooter>
          <Button disabled={isLoading} color="primary" onClick={onConfirm}>
            Passer en gestionnaire
          </Button>
          <Button disabled={isLoading} onClick={onBack}>
            Annuler
          </Button>
        </StyledFooter>
      </>
    );
  }

  if (
    selectedMember.membershipType === MEMBERSHIP_TYPES.MANAGER &&
    selectedMembershipType === MEMBERSHIP_TYPES.MEMBER
  ) {
    return (
      <>
        <BackButton disabled={isLoading} onClick={onBack} />
        <StyledTitle>
          Retirer à {selectedMember.displayName} le droit de gestionnaire&nbsp;?
        </StyledTitle>
        <Spacer size="0.5rem" />
        <StyledContent>
          <p>
            Ce membre n'aura plus accès à la liste et aux informations des
            membres du groupe, ne pourra plus modifier les informations du
            groupe ni créer des événements au nom du groupe
          </p>
          <p>
            {selectedMember.displayName} restera parmi les membres actifs de
            votre groupe.
          </p>
        </StyledContent>
        <Spacer size="1rem" />
        <StyledFooter>
          <Button disabled={isLoading} color="danger" onClick={onConfirm}>
            Retirer le droit de gestionnaire
          </Button>
          <Button disabled={isLoading} onClick={onBack}>
            Annuler
          </Button>
        </StyledFooter>
      </>
    );
  }

  return null;
};

ConfirmPanel.propTypes = {
  selectedMember: PropTypes.shape({
    displayName: PropTypes.string,
    gender: PropTypes.string,
    membershipType: PropTypes.oneOf([
      MEMBERSHIP_TYPES.MEMBER,
      MEMBERSHIP_TYPES.FOLLOWER,
      MEMBERSHIP_TYPES.MANAGER,
    ]),
  }),
  selectedMembershipType: PropTypes.oneOf([
    MEMBERSHIP_TYPES.MEMBER,
    MEMBERSHIP_TYPES.FOLLOWER,
    MEMBERSHIP_TYPES.MANAGER,
  ]),
  onBack: PropTypes.func,
  onConfirm: PropTypes.func,
  isLoading: PropTypes.bool,
};

export default ConfirmPanel;
