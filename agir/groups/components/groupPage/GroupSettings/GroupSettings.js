import PropTypes from "prop-types";
import React from "react";

import styled from "styled-components";

import GroupMember from "./GroupMember";
import ShareLink from "./ShareLink";
import GroupInvitation from "./GroupInvitation";
import AddPair from "./AddPair";
import Spacer from "@agir/front/genericComponents/Spacer.js";

import group_illustration from "@agir/front/genericComponents/images/group_illustration.svg";

import ManagementMenu from "@agir/events/eventManagement/ManagementMenu.js";
import ManagementPanel from "@agir/events/eventManagement/ManagementPanel.js";

// import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
// import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";
// import DesktopGroupPage, { DesktopGroupPageSkeleton } from "./DesktopGroupPage";
// import MobileGroupPage, { MobileGroupPageSkeleton } from "./MobileGroupPage";

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

export const GroupSettings = (props) => {
  return (
    //   <ResponsiveLayout
    //     {...props}
    //     MobileLayout={MobileGroupSettings}
    //     DesktopLayout={DesktopGroupSettings}
    //   />
    <>
      <ManagementMenu title="Cortège France insoumise à la marche contre la fourrure 2020" />
      <ManagementPanel
        title={DEFAULT_MEMBERS.length + " Membres"}
        subtitle="Animateurs et animatrices"
        onBack={() => console.log("ON BACK MENU")}
        illustration={group_illustration}
      >

        <ShareLink
          label="Copier les mails des membres"
          color="secondary"
          url={DEFAULT_EMAILS.join(", ")}
        />

        <Spacer size="1rem" />
        
        {DEFAULT_MEMBERS.map((e, id) => (
          <>
          <GroupMember
            key={id}
            name={e.name}
            role={e.role}
            email={e.email}
            assets={e.assets}
          />
          <Spacer size="0.5rem" />
          </>
        ))}

        <Spacer size="1rem" />
        
        <ShareLink
          label="Copier"
          url="actionpopulaire.fr/groupe/id"
          title="Partagez le lien public de l'équipe"
        />

        <Spacer size="1rem" />
        <GroupInvitation
          title={
            <>
              Invitez de nouveaux membres{" "}
              <InlineBlock>dans votre équipe !</InlineBlock>
            </>
          }
        />

        <Spacer size="1rem" />
        <AddPair />
      </ManagementPanel>
    </>
  );
};
GroupSettings.propTypes = {
  isLoading: PropTypes.bool,
  activeTab: PropTypes.string,
};
export default GroupSettings;
