import PropTypes from "prop-types";
import React from "react";

import GroupMember from "./GroupMember";
import ShareLink from "./ShareLink";
import GroupInvitation from "./GroupInvitation";
import AddPair from "./AddPair";

// import ManagementMenu from "@agir/events/components/eventManagement/ManagementMenu.js";
// import ManagementPanel from "@agir/events/components/eventManagement/ManagementPanel.js";

import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";
// import DesktopGroupPage, { DesktopGroupPageSkeleton } from "./DesktopGroupPage";
// import MobileGroupPage, { MobileGroupPageSkeleton } from "./MobileGroupPage";

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
      {DEFAULT_MEMBERS.map((e, id) => (
        <GroupMember
          key={id}
          name={e.name}
          role={e.role}
          email={e.email}
          assets={e.assets}
        />
      ))}
      <ShareLink
        label="Copier les mails des membres"
        color="secondary"
        url={DEFAULT_EMAILS.join(",")}
        title={DEFAULT_EMAILS.length + " Membres"}
      />
      <ShareLink
        label="Copier"
        url="actionpopulaire.fr/groupe/id"
        title="Partagez le lien public de l'équipe"
      />
      <GroupInvitation title="Invitez de nouveaux membres dans votre équipe !" />
      <AddPair />
    </>
  );
};
GroupSettings.propTypes = {
  isLoading: PropTypes.bool,
  activeTab: PropTypes.string,
};
export default GroupSettings;
