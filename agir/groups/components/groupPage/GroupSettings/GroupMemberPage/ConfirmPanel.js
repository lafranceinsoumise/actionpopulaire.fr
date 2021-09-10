import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import BackButton from "@agir/front/genericComponents/ObjectManagement/BackButton";
import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

import { StyledTitle } from "@agir/groups/groupPage/GroupSettings/styledComponents";

import { MEMBERSHIP_TYPES } from "@agir/groups/utils/group";
import { getGenderedWord } from "@agir/lib/utils/display";

const StyledContent = styled.div`
  p {
    color: ${(props) => props.theme.black700};
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

  return (
    <>
      <BackButton disabled={isLoading} onClick={onBack} />
      <StyledTitle>
        {selectedMembershipType === MEMBERSHIP_TYPES.MEMBER
          ? `Passer ${selectedMember?.displayName} en membre actif`
          : `Retirer ${selectedMember?.displayName} des membres actifs`}
        &nbsp;?
      </StyledTitle>
      <Spacer size="0.5rem" />
      <StyledContent>
        {selectedMembershipType === MEMBERSHIP_TYPES.MEMBER ? (
          <p>
            Ce membre pourra accéder aux messages du groupe destinés aux membres
            actifs.
          </p>
        ) : (
          <>
            <p>
              Cette personne ne sera plus considérée comme un membre actif de
              votre groupe.
            </p>
            <p>
              {getGenderedWord(
                selectedMember?.gender,
                "Ce membre",
                "Elle",
                "Il"
              )}{" "}
              ne recevra plus les messages postés sur Action Populaire que vous
              destinez aux membres actifs.
            </p>
            <p>
              {selectedMember?.displayName} restera abonné·e à votre groupe.
            </p>
          </>
        )}
      </StyledContent>
      <Spacer size="1rem" />
      <StyledFooter>
        {selectedMembershipType === MEMBERSHIP_TYPES.MEMBER ? (
          <Button disabled={isLoading} color="primary" onClick={onConfirm}>
            Passer en actif
          </Button>
        ) : (
          <Button disabled={isLoading} color="danger" onClick={onConfirm}>
            Retirer
          </Button>
        )}
        <Button disabled={isLoading} onClick={onBack}>
          Annuler
        </Button>
      </StyledFooter>
    </>
  );
};

ConfirmPanel.propTypes = {
  selectedMember: PropTypes.object,
  selectedMembershipType: PropTypes.oneOf([
    MEMBERSHIP_TYPES.MEMBER,
    MEMBERSHIP_TYPES.FOLLOWER,
  ]),
  onBack: PropTypes.func,
  onConfirm: PropTypes.func,
  isLoading: PropTypes.bool,
};

export default ConfirmPanel;
