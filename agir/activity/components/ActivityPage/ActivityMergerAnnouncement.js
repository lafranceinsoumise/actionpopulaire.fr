import React from "react";

import illustration from "@agir/activity/images/activitymergerannouncement.svg";
import CustomAnnouncementCard from "@agir/activity/common/CustomAnnouncementCard";

const ActivityMergerAnnouncement = () => (
  <CustomAnnouncementCard
    slug="ActivityMergerAnnouncement"
    title="Voici vos notifications !"
    illustration={illustration}
  >
    <span>
      Nous avons fusionné la page “À faire” et “Actualités” pour vous simplifier
      la vie.
    </span>
  </CustomAnnouncementCard>
);

export default ActivityMergerAnnouncement;
