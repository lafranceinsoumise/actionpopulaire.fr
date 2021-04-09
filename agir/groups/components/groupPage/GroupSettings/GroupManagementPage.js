import React from "react";

import GroupMember from "./GroupMember";
import AddPair from "./AddPair";
import Spacer from "@agir/front/genericComponents/Spacer.js";

import { DEFAULT_MEMBERS } from "./mock-group.js";
import { StyledTitle } from "./styledComponents.js";

const GroupManagementPage = () => {
  return (
    <>
      <StyledTitle>Animateurs et animatrices</StyledTitle>

      <GroupMember
        name={DEFAULT_MEMBERS[0].name}
        role={DEFAULT_MEMBERS[0].role}
        email={DEFAULT_MEMBERS[0].email}
        assets={DEFAULT_MEMBERS[0].assets}
      />
      <Spacer size="1rem" />
      <AddPair />
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
      <AddPair />
    </>
  );
};

export default GroupManagementPage;
