import React from "react";

import styled from "styled-components";

import GroupMember from "./GroupMember";
import ShareLink from "@agir/front/genericComponents/ShareLink.js";
import GroupInvitation from "./GroupInvitation";
import AddPair from "./AddPair";
import Spacer from "@agir/front/genericComponents/Spacer.js";

import { DEFAULT_EMAILS, DEFAULT_MEMBERS } from "./mock-group.js";
import { StyledTitle } from "./styledComponents.js";

const InlineBlock = styled.div`
  display: inline-block;
`;

const GroupMemberPage = () => {
  return (
    <>
      <StyledTitle>{DEFAULT_MEMBERS.length} Membres</StyledTitle>

      <ShareLink
        label="Copier les mails des membres"
        color="secondary"
        url={DEFAULT_EMAILS.join(", ")}
      />

      <Spacer size="2rem" />

      {DEFAULT_MEMBERS.map((e, id) => (
        <>
          <GroupMember
            key={id}
            name={e.name}
            role={e.role}
            email={e.email}
            assets={e.assets}
          />
          <Spacer size="1rem" />
        </>
      ))}

      <Spacer size="2rem" />

      <ShareLink
        label="Copier"
        url="actionpopulaire.fr/groupe/id"
        title="Partagez le lien public de l'équipe"
      />

      <Spacer size="2rem" />
      <GroupInvitation
        title={
          <>
            Invitez de nouveaux membres{" "}
            <InlineBlock>dans votre équipe !</InlineBlock>
          </>
        }
      />

      <Spacer size="2rem" />
      <AddPair />
    </>
  );
};

export default GroupMemberPage;
