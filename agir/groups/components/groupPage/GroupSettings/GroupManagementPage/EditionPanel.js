import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import GroupMember from "@agir/groups/groupPage/GroupSettings/GroupMember";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import SelectField from "@agir/front/formComponents/SelectField";
import Button from "@agir/front/genericComponents/Button";
import BackButton from "@agir/front/genericComponents/ObjectManagement/BackButton.js";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Toast from "@agir/front/genericComponents/Toast";

import { StyledTitle } from "@agir/groups/groupPage/GroupSettings/styledComponents.js";

const [REFERENT, MANAGER, MEMBER] = [100, 50, 10];

const StyledList = styled.div`
  display: flex;
  align-items: center;
  div {
    display: inline-flex;
    width: 0.5rem;
    height: 0.5rem;
    background-color: ${style.primary500};
    border-radius: 2rem;
    margin-right: 0.5rem;
  }
`;

const StyledHelper = styled.div`
  display: flex;
  padding: 1rem;
  background-color: ${style.black100};
`;

const EditionPanel = (props) => {
  const {
    members,
    onBack,
    onSubmit,
    selectMember,
    selectedMember,
    selectedMembershipType,
    errors,
    isLoading,
    is2022,
  } = props;

  const candidates = useMemo(
    () =>
      members && selectedMembershipType
        ? members.filter((m) => selectedMembershipType !== m.membershipType)
        : [],
    [members, selectedMembershipType]
  );

  return (
    <>
      <BackButton onClick={onBack} />
      <StyledTitle>
        {selectedMembershipType === REFERENT
          ? "Ajouter un binôme animateur"
          : "Ajouter un·e gestionnaire"}
      </StyledTitle>
      <Spacer size="1rem" />
      {candidates.length === 0 ? (
        <StyledHelper style={{ backgroundColor: style.secondary500 }}>
          <RawFeatherIcon
            width="1rem"
            height="1rem"
            name="alert-circle"
            style={{ marginRight: "0.5rem", display: "inline" }}
          />
          Il manque des membres à votre {is2022 ? "équipe" : "groupe"} pour leur
          ajouter ce rôle
        </StyledHelper>
      ) : (
        <>
          <Spacer size="1rem" />
          <SelectField
            label="Choisir un membre"
            placeholder="Sélection"
            options={candidates.map((candidate) => ({
              label: `${candidate.displayName} (${candidate.email})`,
              value: candidate,
            }))}
            onChange={selectMember}
          />
        </>
      )}
      {selectedMember && (
        <>
          <Spacer size="1rem" />
          <GroupMember
            name={selectedMember?.displayName}
            image={selectedMember?.image}
            membershipType={selectedMember?.membershipType}
            email={selectedMember?.email}
            assets={selectedMember?.assets}
          />
          <Spacer size="1rem" />
          <div>
            Ce membre pourra :
            <Spacer size="0.5rem" />
            {selectedMembershipType === REFERENT && (
              <StyledList>
                <div />
                Modifier les permissions des gestionnaires
              </StyledList>
            )}
            <StyledList>
              <div />
              Voir la liste des membres
            </StyledList>
            <StyledList>
              <div />
              Modifier les informations {is2022 ? "de l'équipe" : "du groupe"}
            </StyledList>
            <StyledList>
              <div />
              Créer des événements au nom {is2022 ? "de l'équipe" : "du groupe"}
            </StyledList>
          </div>
          {(errors?.email || errors?.role) && (
            <Toast>Erreur : {errors.email || errors.role}</Toast>
          )}
          <Spacer size="1rem" />
          <Button color="secondary" onClick={onSubmit} disabled={isLoading}>
            Confirmer
          </Button>
        </>
      )}
    </>
  );
};

EditionPanel.propTypes = {
  members: PropTypes.arrayOf(PropTypes.object),
  onBack: PropTypes.func,
  selectMember: PropTypes.func,
  onSubmit: PropTypes.func,
  selectedMember: PropTypes.object,
  selectedMembershipType: PropTypes.oneOf([REFERENT, MANAGER, MEMBER]),
  errors: PropTypes.object,
  isLoading: PropTypes.bool,
  is2022: PropTypes.bool,
};

export default EditionPanel;
