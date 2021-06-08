import React from "react";

import illustration from "@agir/groups/groupPage/images/display-name-announcement-bg.svg";

import Link from "@agir/front/app/Link";

import CustomAnnouncementCard from "@agir/activity/common/CustomAnnouncementCard";

const DisplayNameAnnouncement = () => (
  <CustomAnnouncementCard
    slug="DisplayNameAnnouncement"
    title="Nouveau : nom d'affichage et avatar"
    illustration={illustration}
  >
    <span>
      Pour que les autres puissent vous reconnaitre, prenez le temps de{" "}
      <Link route="personalInformation">
        modifier ces informations dans votre profil
      </Link>
      .
    </span>
  </CustomAnnouncementCard>
);

export default DisplayNameAnnouncement;
