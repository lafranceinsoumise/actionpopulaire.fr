import React, { useState } from "react";

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

import { DEFAULT_MEMBERS } from "./mock-group.js";
import { StyledTitle } from "./styledComponents.js";

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

const [CONFIG_PAIR, CONFIG_MANAGER] = [1, 2];

const GroupManagementPage = (props) => {
  const { onBack, illustration } = props;
  const [config, setConfig] = useState(null);

  if (CONFIG_PAIR === config)
    return (
      <>
        <BackButton
          onBack={() => {
            setConfig(null);
          }}
        />

        <StyledTitle>Ajouter un binôme animateur</StyledTitle>
        <Spacer size="1rem" />
        <SelectField label="Choisir un membre" options={[1, 2, 3]} />

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

        <GroupMember
          name={DEFAULT_MEMBERS[0].name}
          email={DEFAULT_MEMBERS[0].email}
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
            Modifier les informations du groupe
          </StyledList>
          <StyledList>
            <div />
            Créer des événements au nom du groupe
          </StyledList>
        </div>
        <Spacer size="1rem" />
        <Button color="secondary">Confirmer</Button>
      </>
    );

  if (CONFIG_MANAGER === config)
    return (
      <>
        <BackButton
          onBack={() => {
            setConfig(null);
          }}
        />

        <StyledTitle>Ajouter un gestionnaire</StyledTitle>
        <Spacer size="1rem" />
        <SelectField label="Choisir un membre" options={[1, 2, 3]} />

        <Spacer size="1rem" />

        <GroupMember
          name={DEFAULT_MEMBERS[0].name}
          email={DEFAULT_MEMBERS[0].email}
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
            Modifier les informations du groupe
          </StyledList>
          <StyledList>
            <div />
            Créer des événements au nom du groupe
          </StyledList>
        </div>
      </>
    );

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Animateurs et animatrices</StyledTitle>

      <GroupMember
        name={DEFAULT_MEMBERS[0].name}
        role={DEFAULT_MEMBERS[0].role}
        email={DEFAULT_MEMBERS[0].email}
        assets={DEFAULT_MEMBERS[0].assets}
      />
      <Spacer size="1rem" />
      <AddPair
        label="Ajouter votre binôme"
        onClick={() => {
          setConfig(CONFIG_PAIR);
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
