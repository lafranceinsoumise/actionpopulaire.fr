import React, { useEffect, useState, useCallback } from "react";

import GroupMember from "./GroupMember";
import AddPair from "./AddPair";
import HeaderPanel from "./HeaderPanel";
import Spacer from "@agir/front/genericComponents/Spacer.js";
import SelectField from "@agir/front/formComponents/SelectField";
import Button from "@agir/front/genericComponents/Button";
import BackButton from "@agir/front/genericComponents/ObjectManagement/BackButton.js";
import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Toast from "@agir/front/genericComponents/Toast";

import { StyledTitle } from "./styledComponents.js";

import { getMembers, addRoleToMember } from "@agir/groups/groupPage/api.js";
import { useGroup } from "@agir/groups/groupPage/hooks/group.js";

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

const [GROUP_IS_2022, GROUP_LFI] = ["de l'équipe", "du groupe"];

const [CONFIG_REFERENT, CONFIG_MANAGER] = [1, 2];
const [MEMBER, MANAGER, REFERENT] = [10, 50, 100];

const GroupManagementPage = (props) => {
  const { onBack, illustration, groupPk } = props;
  const [config, setConfig] = useState(null);
  const [errors, setErrors] = useState({});

  const [members, setMembers] = useState([]);
  const [newMemberManager, setNewMemberManager] = useState(null);
  const [newMemberReferent, setNewMemberReferent] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const group = useGroup(groupPk);

  const getMembersAPI = async (groupPk) => {
    const { data } = await getMembers(groupPk);
    setMembers(data);
  };

  const handleNewManagerChange = useCallback((e) => {
    setNewMemberManager(e.value);
  }, []);

  const handleNewReferentChange = useCallback((e) => {
    setNewMemberReferent(e.value);
  }, []);

  const submitNewManager = useCallback(async () => {
    setErrors({});
    setIsLoading(true);
    const res = await addRoleToMember(groupPk, {
      email: newMemberManager,
      role: "manager",
    });
    setIsLoading(false);
    if (!!res.error) {
      setErrors(res.error);
      return;
    }
    setConfig(null);
  }, [groupPk, newMemberManager]);

  const submitNewReferent = useCallback(async () => {
    setErrors({});
    setIsLoading(true);
    const res = await addRoleToMember(groupPk, {
      email: newMemberReferent,
      role: "referent",
    });
    setIsLoading(false);
    if (!!res.error) {
      setErrors(res.error);
      return;
    }
    setConfig(null);
  }, [groupPk, newMemberReferent]);

  useEffect(() => {
    getMembersAPI(groupPk);
  }, [groupPk]);

  if (CONFIG_REFERENT === config)
    return (
      <>
        <BackButton
          onClick={() => {
            setNewMemberReferent(null);
            setErrors({});
            setConfig(null);
          }}
        />

        <StyledTitle>Ajouter un binôme animateur</StyledTitle>
        <Spacer size="1rem" />

        {members.filter((m) => REFERENT !== m.membershipType).length === 0 ? (
          <StyledHelper style={{ backgroundColor: style.secondary500 }}>
            <RawFeatherIcon
              width="1rem"
              height="1rem"
              name="alert-circle"
              style={{ marginRight: "0.5rem", display: "inline" }}
            />
            Il manque des membres à votre
            {" " + (group.is2022 ? "équipe" : "groupe") + " "} pour leur ajouter
            ce rôle
          </StyledHelper>
        ) : (
          <>
            <Spacer size="1rem" />
            <SelectField
              label="Choisir un membre"
              placeholder="Sélection"
              options={members
                .filter((m) => REFERENT !== m.membershipType)
                .map((m) => {
                  return { label: `${m.displayName} (${m.email})`, value: m };
                })}
              onChange={handleNewReferentChange}
            />
          </>
        )}

        {newMemberReferent && (
          <>
            <Spacer size="1rem" />

            <StyledHelper>
              <RawFeatherIcon
                width="1rem"
                height="1rem"
                name="alert-circle"
                style={{ marginRight: "0.5rem", display: "inline" }}
              />
              Pour respecter la charte des équipes de soutien, votre{" "}
              {" " + (group.is2022 ? "équipe" : "groupe") + " "}
              devrait être animée à parité de genre.
            </StyledHelper>

            <Spacer size="1rem" />

            <GroupMember
              name={newMemberReferent?.displayName}
              image={newMemberReferent?.image}
              membershipType={newMemberReferent?.membershipType}
              email={newMemberReferent?.email}
              assets={newMemberReferent?.assets}
            />
            <Spacer size="1rem" />

            <div>
              Ce membre pourra :
              <Spacer size="0.5rem" />
              <StyledList>
                <div />
                Modifier les permissions des gestionnaires
              </StyledList>
              <StyledList>
                <div />
                Voir la liste des membres
              </StyledList>
              <StyledList>
                <div />
                Modifier les informations
                {" " + (group.is2022 ? GROUP_IS_2022 : GROUP_LFI)}
              </StyledList>
              <StyledList>
                <div />
                Créer des événements au nom
                {" " + (group.is2022 ? GROUP_IS_2022 : GROUP_LFI)}
              </StyledList>
            </div>

            {errors?.email ||
              (errors?.role && (
                <>
                  <Toast>Erreur : {errors?.email || errors?.role}</Toast>
                </>
              ))}

            <Spacer size="1rem" />
            <Button
              color="secondary"
              onClick={submitNewReferent}
              disabled={isLoading}
            >
              Confirmer
            </Button>
          </>
        )}
      </>
    );

  if (CONFIG_MANAGER === config)
    return (
      <>
        <BackButton
          onClick={() => {
            setNewMemberManager(null);
            setErrors({});
            setConfig(null);
          }}
        />

        <StyledTitle>Ajouter un·e gestionnaire</StyledTitle>
        <Spacer size="1rem" />

        {members.filter((m) => ![MANAGER, REFERENT].includes(m.membershipType))
          .length === 0 ? (
          <StyledHelper style={{ backgroundColor: style.secondary500 }}>
            <RawFeatherIcon
              width="1rem"
              height="1rem"
              name="alert-circle"
              style={{ marginRight: "0.5rem", display: "inline" }}
            />
            Il manque des membres à votre
            {" " + (group.is2022 ? "équipe" : "groupe") + " "}pour leur ajouter
            ce rôle
          </StyledHelper>
        ) : (
          <SelectField
            label="Choisir un membre"
            placeholder="Sélection"
            options={members
              .filter((m) => ![MANAGER, REFERENT].includes(m.membershipType))
              .map((m) => {
                return { label: `${m.displayName} (${m.email})`, value: m };
              })}
            onChange={handleNewManagerChange}
          />
        )}

        {newMemberManager && (
          <>
            <Spacer size="1rem" />

            <GroupMember
              name={newMemberManager?.displayName}
              image={newMemberManager?.image}
              membershipType={newMemberManager?.membershipType}
              email={newMemberManager?.email}
              assets={newMemberManager?.assets}
            />

            <Spacer size="1rem" />
            <div>
              Ce membre pourra :
              <Spacer size="0.5rem" />
              <StyledList>
                <div />
                Voir la liste des membres
              </StyledList>
              <StyledList>
                <div />
                Modifier les informations
                {" " + (group.is2022 ? GROUP_IS_2022 : GROUP_LFI)}
              </StyledList>
              <StyledList>
                <div />
                Créer des événements au nom
                {" " + (group.is2022 ? GROUP_IS_2022 : GROUP_LFI)}
              </StyledList>
            </div>

            {errors?.email ||
              (errors?.role && (
                <>
                  <Toast>Erreur : {errors?.email || errors?.role}</Toast>
                </>
              ))}

            <Spacer size="1rem" />
            <Button
              color="secondary"
              onClick={submitNewManager}
              disabled={isLoading}
            >
              Confirmer
            </Button>
          </>
        )}
      </>
    );

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Animateurs et animatrices</StyledTitle>

      <Spacer size="0.5rem" />

      {members.map(
        (member, id) =>
          REFERENT === member.membershipType && (
            <>
              <GroupMember
                key={id}
                name={member?.displayName}
                image={member?.image}
                membershipType={member?.membershipType}
                email={member?.email}
                assets={member?.assets}
              />
              <Spacer size="1rem" />
            </>
          )
      )}

      {members.filter((member) => REFERENT === member.membershipType).length <
        2 && (
        <>
          <AddPair
            label="Ajouter votre binôme"
            onClick={() => {
              setConfig(CONFIG_REFERENT);
            }}
          />
          <Spacer size="2rem" />
        </>
      )}

      <span>
        Les animateur·ices organisent la vie
        {" " + (group.is2022 ? GROUP_IS_2022 : GROUP_LFI)}. Pour respecter la
        charte des équipes de soutien, votre{" "}
        {" " + (group.is2022 ? "équipe" : "groupe") + " "} doit être animée à
        parité de genre.
      </span>

      <Spacer size="1rem" />

      <StyledTitle>Gestionnaires</StyledTitle>

      <span>
        Ajoutez des gestionnaires pour vous assiter sur la gestion
        {" " + (group.is2022 ? GROUP_IS_2022 : GROUP_LFI)} au quotidien sur la
        plate-forme. Ces derniers ont accès à la liste des membres, peuvent
        modifier les informations
        {" " + (group.is2022 ? GROUP_IS_2022 : GROUP_LFI)}, et créer des
        événements au nom{" " + (group.is2022 ? GROUP_IS_2022 : GROUP_LFI)}.
      </span>

      <Spacer size="1rem" />

      {members.map(
        (member, id) =>
          MANAGER === member.membershipType && (
            <>
              <GroupMember
                key={id}
                name={member?.displayName}
                image={member?.image}
                membershipType={member?.membershipType}
                email={member?.email}
                assets={member?.assets}
              />
              <Spacer size="1rem" />
            </>
          )
      )}

      <AddPair
        label="Ajouter un·e gestionnaire"
        onClick={() => {
          setConfig(CONFIG_MANAGER);
        }}
      />

      <hr />

      <a href="https://actionpopulaire.fr/formulaires/demande-changement-animation-ga/">
        Changer l’animation{" " + (group.is2022 ? GROUP_IS_2022 : GROUP_LFI)}
      </a>
      <Spacer size="0.5rem" />
      <a href="https://infos.actionpopulaire.fr/contact/">
        Je ne souhaite plus être animateur ou animatrice
      </a>
      <Spacer size="0.5rem" />
      <a
        href="https://agir.lafranceinsoumise.fr/formulaires/demande-suppression-ga/"
        style={{ color: style.redNSP }}
      >
        Supprimer {" " + group.is2022 ? "l'équipe" : "le groupe"}
      </a>
    </>
  );
};

export default GroupManagementPage;
