import PropTypes from "prop-types";
import React, { useCallback, useEffect, useMemo, useState } from "react";
import styled from "styled-components";

import CheckboxField from "@agir/front/formComponents/CheckboxField";
import RadioField from "@agir/front/formComponents/RadioField";
import SelectField from "@agir/front/formComponents/SelectField";
import Button from "@agir/front/genericComponents/Button";
import { Hide } from "@agir/front/genericComponents/grid";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import BackButton from "@agir/front/genericComponents/ObjectManagement/BackButton";
import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents";
import Spacer from "@agir/front/genericComponents/Spacer";
import GroupMemberList from "@agir/groups/groupPage/GroupSettings/GroupMemberList";
import ReferentReplacementWarning from "./ReferentReplacementWarning";

import {
  MEMBERSHIP_TYPES,
  getGenderedMembershipType,
} from "@agir/groups/utils/group";

const StyledWarning = styled.p`
  margin: 0;
  display: flex;
  gap: 1rem;
  font-size: 0.875rem;
  font-weight: 400;
  line-height: 1.3;
  color: ${(props) => props.theme.redNSP};

  & > * {
    flex: 1 1 auto;
  }
  & > :first-child {
    flex: 0 0 auto;
  }
`;

const StyledSuccess = styled.p`
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 1rem;
  background-color: ${(props) => props.theme.green100};
  font-weight: 600;
  padding: 0.5rem 1rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    font-size: 0.875rem;
  }

  & > * {
    flex: 0 0 auto;
  }

  ${RawFeatherIcon} {
    color: ${(props) => props.theme.green500};
  }
`;

const StyledSelect = styled(SelectField)`
  .select__control {
    background-color: ${(props) => props.theme.black50};
    min-height: 54px;
    gap: 0.25rem;

    &:focus {
      border-color: ${({ $invalid, theme }) =>
        $invalid ? theme.redNSP : theme.black200};
    }

    &::placeholder {
      color: ${(props) => props.theme.black700};
    }

    ${RawFeatherIcon} {
      width: 2.5rem;

      svg {
        width: 1.5rem;
        height: 1.5rem;
      }
    }
  }
`;

const PanelContent = styled.div``;

const ReferentReplacementPanel = (props) => {
  const {
    group,
    leavingMember,
    members,
    error,
    isLoading,
    isDone,
    onBack,
    onSubmit,
  } = props;

  const [step, setStep] = useState("form");
  const [replacement, setReplacement] = useState(null);
  const [newMembershipType, setNewMembershipType] = useState(null);
  const [agreement, setAgreement] = useState(false);
  const [errors, setErrors] = useState(null);

  const memberChoices = useMemo(
    () =>
      Array.isArray(members)
        ? members
            .filter(
              (member) =>
                member.id !== leavingMember.id &&
                (member.membershipType === MEMBERSHIP_TYPES.MEMBER ||
                  member.membershipType === MEMBERSHIP_TYPES.MANAGER),
            )
            .map((member) => ({
              ...member,
              value: member.id,
              label: `${member.displayName} <${member.email}>`,
            }))
            .sort(
              (a, b) => parseInt(b.membershipType) - parseInt(a.membershipType),
            )
        : [],
    [leavingMember, members],
  );

  const membershipTypeChoices = useMemo(
    () => [
      ...Object.values(MEMBERSHIP_TYPES)
        .sort((a, b) => b - a)
        .filter(
          (membershipType) => membershipType !== MEMBERSHIP_TYPES.REFERENT,
        )
        .map((membershipType) => ({
          value: String(membershipType),
          label: getGenderedMembershipType(membershipType),
        })),
      {
        value: 0,
        label: "Part du groupe",
      },
    ],
    [],
  );

  const handleChangeReplacement = useCallback((value) => {
    setReplacement(value);
    setErrors((state) => ({ ...state, replacement: undefined }));
  }, []);

  const handleChangeNewMembershipType = useCallback((value) => {
    setNewMembershipType(value);
    setErrors((state) => ({ ...state, newMembershipType: undefined }));
  }, []);

  const handleCheckAgreement = useCallback((e) => {
    setAgreement(e.target.checked);
  }, []);

  const handleSubmit = useCallback(
    (e) => {
      e && e.preventDefault();
      switch (step) {
        case "form": {
          setErrors(null);
          const errors = {};
          if (replacement === null) {
            errors.replacement = "Veuillez sélectionner une personne";
          }
          if (newMembershipType === null) {
            errors.newMembershipType =
              "Veuillez sélectionner une option avant de continuer";
          }
          if (Object.keys(errors).length === 0) {
            setStep("confirmation");
          } else {
            setErrors(errors);
          }
          break;
        }
        case "confirmation": {
          if (!agreement) {
            return;
          }
          onSubmit && onSubmit(replacement, newMembershipType);
          break;
        }
        case "success": {
          setReplacement(null);
          setNewMembershipType(null);
          setAgreement(false);
          onBack && onBack();
          setStep("form");
          break;
        }
      }
    },
    [step, onSubmit, replacement, newMembershipType, agreement, onBack],
  );

  const handleBack = useCallback(() => {
    switch (step) {
      case "confirmation":
        setStep("form");
        break;
      default:
        onBack && onBack();
        break;
    }
  }, [step, onBack]);

  useEffect(() => isDone && setStep("success"), [isDone]);

  return (
    <>
      <BackButton onClick={handleBack}>Back !</BackButton>
      <Hide $under>
        <StyledTitle>Changer l'animation</StyledTitle>
        <Spacer size="2rem" />
      </Hide>
      {step === "form" && (
        <PanelContent>
          <ReferentReplacementWarning group={group} />
          <Spacer size="2rem" />
          {group.isCertified && (
            <>
              <StyledWarning>
                <RawFeatherIcon
                  width="1rem"
                  height="1rem"
                  name="alert-circle"
                />
                Si vous partez sans personne pour vous remplacer à l'animation,
                le groupe perdra sa certification
              </StyledWarning>
              <Spacer size="2rem" />
            </>
          )}
          <form onSubmit={handleSubmit}>
            <StyledSelect
              isSearchable
              searchIcon
              label="Qui vous remplace ?"
              helpText={
                <small>La personne doit être membre actif du groupe</small>
              }
              value={replacement}
              options={memberChoices}
              onChange={handleChangeReplacement}
              placeholder="Rechercher un membre du groupe"
              error={errors?.replacement}
            />
            <Spacer size="2rem" />
            <RadioField
              label="Quel rôle voulez-vous avoir une fois l'animation quittée ?"
              options={membershipTypeChoices}
              value={newMembershipType}
              onChange={handleChangeNewMembershipType}
              error={errors?.newMembershipType}
            />
            <Spacer size="2rem" />
            <Button type="submit" block color="primary">
              Continuer
            </Button>
          </form>
        </PanelContent>
      )}

      {step === "confirmation" && (
        <PanelContent>
          <h4>Qui part ?</h4>
          <GroupMemberList members={[leavingMember]} />
          <Spacer size="2rem" />
          <h4>Qui vous remplace ?</h4>
          <GroupMemberList members={[replacement]} />
          <Spacer size="2rem" />
          <h4>Que devient la personne qui part de l'animation ?</h4>
          <p>
            {newMembershipType === "0"
              ? "Vous partez du groupe"
              : `Vous restez dans le groupe, en tant que ${getGenderedMembershipType(newMembershipType).toLowerCase()}`}
          </p>
          <Spacer size="2rem" />
          <CheckboxField
            label="Je certifie que cette décision a été concertée et acceptée par les autres membres de mon groupe, à commencer par les animateurs·rices actuel·les et futur·es du groupe."
            value={agreement}
            onChange={handleCheckAgreement}
            disabled={isLoading}
          />
          <Spacer size="2rem" />
          {error && (
            <>
              <StyledWarning style={{ display: "block", textAlign: "center" }}>
                {error}
              </StyledWarning>
              <Spacer size="2rem" />
            </>
          )}
          <Button
            onClick={handleSubmit}
            block
            color="primary"
            icon="send"
            disabled={isLoading || !agreement}
            loading={isLoading}
          >
            Continuer
          </Button>
        </PanelContent>
      )}

      {step === "success" && (
        <PanelContent>
          <StyledSuccess>
            <RawFeatherIcon name="check" />
            Votre demande a été enregistrée !
          </StyledSuccess>
          <Spacer size="2rem" />
          <p style={{ textAlign: "center" }}>
            La personne qui co-anime avec vous et la nouvelle personne ont été
            notifiées. Après leur validation, la demande de changement sera
            envoyée au Pôle des Groupes d'action qui l’actera.
          </p>
          <Spacer size="2rem" />
          <Button
            onClick={handleSubmit}
            block
            color="primary"
            disabled={isLoading}
            loading={isLoading}
          >
            Terminer
          </Button>
        </PanelContent>
      )}
    </>
  );
};

ReferentReplacementPanel.propTypes = {
  group: PropTypes.object,
  leavingMember: PropTypes.object,
  members: PropTypes.arrayOf(PropTypes.object),
  error: PropTypes.string,
  isLoading: PropTypes.bool,
  isDone: PropTypes.bool,
  onBack: PropTypes.func,
  onSubmit: PropTypes.func,
};

export default ReferentReplacementPanel;
