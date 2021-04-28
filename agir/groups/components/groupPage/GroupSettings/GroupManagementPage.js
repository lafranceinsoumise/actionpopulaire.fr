import React, { useEffect, useState } from "react";

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

import { StyledTitle } from "./styledComponents.js";

import { getMembers, addRoleToMember } from "@agir/groups/groupPage/api.js";

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

const [CONFIG_REFERENT, CONFIG_MANAGER] = [1, 2];
const [MEMBER, MANAGER, REFERENT] = [10, 50, 100];

const GroupManagementPage = (props) => {
  const { onBack, illustration, groupPk } = props;
  const [config, setConfig] = useState(null);

  const [members, setMembers] = useState([]);
  const [newMemberManager, setNewMemberManager] = useState(null);
  const [newMemberReferent, setNewMemberReferent] = useState(null);

  const getMembersAPI = async (groupPk) => {
    const { data } = await getMembers(groupPk);
    console.log("get members from group : ", data);
    setMembers(data);
  };

  const handleNewManagerChange = (e) => {
    setNewMemberManager(e.value);
  };

  const handleNewReferentChange = (e) => {
    setNewMemberReferent(e.value);
  };

  const submitNewManager = async () => {
    const res = await addRoleToMember(groupPk, {
      email: newMemberManager,
      role: "manager",
    });
  };

  const submitNewReferent = async () => {
    const res = await addRoleToMember(groupPk, {
      email: newMemberReferent,
      role: "referent",
    });
  };

  useEffect(() => {
    getMembersAPI(groupPk);
  }, [groupPk]);

  if (CONFIG_REFERENT === config)
    return (
      <>
        <BackButton
          onClick={() => {
            setConfig(null);
          }}
        />

        <StyledTitle>Ajouter un binôme animateur</StyledTitle>
        <Spacer size="1rem" />
        <SelectField
          label="Choisir un membre"
          placeholder="Sélection"
          options={members.map((m) => {
            if (REFERENT === m.membershipType) return;
            return { label: m.email, value: m.email };
          })}
          onChange={handleNewReferentChange}
        />

        <Spacer size="1rem" />

        <StyledHelper>
          <RawFeatherIcon
            width="1rem"
            height="1rem"
            name="alert-circle"
            style={{ marginRight: "0.5rem", display: "inline" }}
          />
          Pour respecter la charte des équipes de soutien, votre équipe devrait
          être animée à parité de genre.
        </StyledHelper>

        <Spacer size="1rem" />

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
            Modifier les informations du groupe
          </StyledList>
          <StyledList>
            <div />
            Créer des événements au nom du groupe
          </StyledList>
        </div>
        <Spacer size="1rem" />
        <Button color="secondary" onClick={submitNewReferent}>
          Confirmer
        </Button>
      </>
    );

  if (CONFIG_MANAGER === config)
    return (
      <>
        <BackButton
          onClick={() => {
            setConfig(null);
          }}
        />

        <StyledTitle>Ajouter un gestionnaire</StyledTitle>
        <Spacer size="1rem" />
        <SelectField
          label="Choisir un membre"
          placeholder="Sélection"
          options={members.map((m) => {
            if (MANAGER === m.membershipType) return;
            return { label: m.email, value: m.email };
          })}
          onChange={handleNewManagerChange}
        />

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
            Modifier les informations du groupe
          </StyledList>
          <StyledList>
            <div />
            Créer des événements au nom du groupe
          </StyledList>
        </div>

        <Spacer size="1rem" />
        <Button color="secondary" onClick={submitNewManager}>
          Confirmer
        </Button>
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

      <AddPair
        label="Ajouter votre binôme"
        onClick={() => {
          setConfig(CONFIG_REFERENT);
        }}
      />
      <Spacer size="2rem" />

      <span>
        Les animateur·ices organisent la vie du groupe. Pour respecter la charte
        des équipes de soutien, votre équipe doit être animée à parité de genre.
      </span>

      <Spacer size="1rem" />

      <StyledTitle>Gestionnaires</StyledTitle>

      <span>
        Ajoutez des gestionnaires pour vous assiter sur la gestion du groupe au
        quotidien sur la plate-forme. Ces derniers ont accès à la liste des
        membres, peuvent modifier les informations du groupe, et créer des
        événements au nom du groupe.
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

      <a href="#">Changer l’animation du groupe</a>
      <Spacer size="0.5rem" />
      <a href="#">Je ne souhaite plus être animateur ou animatrice</a>
      <Spacer size="0.5rem" />
      <a href="#" style={{ color: style.redNSP }}>
        Supprimer le groupe
      </a>
    </>
  );
};

export default GroupManagementPage;
