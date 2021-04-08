import React, { useState, useMemo } from "react";

import group_members from "@agir/front/genericComponents/images/group_members.svg";
import group_financement from "@agir/front/genericComponents/images/group_financement.svg";
import group_general from "@agir/front/genericComponents/images/group_general.svg";

import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import ManagementMenu from "@agir/events/eventManagement/ManagementMenu.js";
import ManagementPanel from "@agir/events/eventManagement/ManagementPanel.js";
import GroupMemberPage from "./GroupMemberPage.js";

// import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
// import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";
// import DesktopGroupPage, { DesktopGroupPageSkeleton } from "./DesktopGroupPage";
// import MobileGroupPage, { MobileGroupPageSkeleton } from "./MobileGroupPage";

const MENU_ITEMS_GROUP = {
  members: {
    id: "members",
    label: "Membres",
    labelFunction: (group) => `${group?.membersCount || ""} Membres`,
    icon: "users",
    component: <GroupMemberPage />,
  },
  management: {
    id: "management",
    label: "Gestion et animation",
    icon: "lock",
    illustration: group_members,
  },
  finance: {
    id: "finance",
    label: "Financement",
    icon: "sun",
    illustration: group_financement,
  },
  general: {
    id: "general",
    label: "Général",
    icon: "file-text",
    illustration: group_general,
  },
  location: {
    id: "location",
    label: "Localisation",
    icon: "map-pin",
  },
  contact: {
    id: "contact",
    label: "Contact",
    icon: "mail",
  },
  links: {
    id: "links",
    label: "Liens et réseaux sociaux",
    icon: "at-sign",
  },
};

export const GroupSettings = (props) => {
  const { group = { membersCount: 3 } } = props;

  const firstItem = Object.keys(MENU_ITEMS_GROUP)[0];
  const [selectedItem, setSelectedItem] = useState(firstItem);

  const label = useMemo(
    () =>
      MENU_ITEMS_GROUP[selectedItem].labelFunction
        ? MENU_ITEMS_GROUP[selectedItem].labelFunction(group)
        : MENU_ITEMS_GROUP[selectedItem].label,
    [group, selectedItem]
  );

  return (
    //   <ResponsiveLayout
    //     {...props}
    //     MobileLayout={MobileGroupSettings}
    //     DesktopLayout={DesktopGroupSettings}
    //   />

    <PageFadeIn ready={true}>
      <ManagementMenu
        title="Cortège France insoumise à la marche contre la fourrure 2020"
        items={MENU_ITEMS_GROUP}
        selectedItem={selectedItem}
        onSelect={setSelectedItem}
      />

      <ManagementPanel
        title={label}
        subtitle={MENU_ITEMS_GROUP[selectedItem].subtitle}
        onBack={() => console.log("ON BACK MENU")}
        illustration={MENU_ITEMS_GROUP[selectedItem].illustration}
      >
        {MENU_ITEMS_GROUP[selectedItem].component}
      </ManagementPanel>
    </PageFadeIn>
  );
};
GroupSettings.propTypes = {};

export default GroupSettings;
