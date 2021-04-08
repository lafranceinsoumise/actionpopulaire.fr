import React from "react";

import styled from "styled-components";

import GroupMember from "./GroupMember";
import ShareLink from "./ShareLink";
import GroupInvitation from "./GroupInvitation";
import AddPair from "./AddPair";
import Spacer from "@agir/front/genericComponents/Spacer.js";

const InlineBlock = styled.div`
  display: inline-block;
`;

const DEFAULT_EMAILS = [
  "test@example.fr",
  "test@example.fr",
  "test@example.fr",
];

const DEFAULT_MEMBERS = [
  {
    name: "Jean-Luc Mélenchon",
    role: "Administrateur",
    email: "jlm@email.fr",
    assets: ["Député", "Journaliste", "Blogueur", "Artiste", "Informaticien"],
  },
  {
    name: "Membre",
    role: "Animatrice",
    email: "example@email.fr",
    assets: ["Journaliste", "Blogueur", "Artiste"],
  },
  {
    name: "Membre",
    role: "Animatrice",
    email: "example@email.fr",
    assets: ["Journaliste", "Blogueur", "Artiste"],
  },
];

const GroupMemberPage = () => {
  return (
    <>
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
