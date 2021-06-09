import React from "react";

import illustration from "@agir/groups/groupPage/images/empty-messages-bg.svg";
import CustomAnnouncementCard from "@agir/activity/common/CustomAnnouncementCard";

const DiscussionAnnouncement = () => (
  <CustomAnnouncementCard slug="DiscussionAnnouncement">
    {({ link }) => (
      <>
        <div
          aria-hidden="true"
          style={{ backgroundImage: `url(${illustration})` }}
        />
        <p>
          <strong>
            Nouveau&nbsp;: discutez de vos prochaines actions ici&nbsp;!
          </strong>
          <span>
            Vos animateur·ices publieront des messages auxquels vous pourrez
            répondre sur cette page.{" "}
            {link ? (
              <a href={link} target="_blank" rel="noopener noreferrer">
                En savoir plus
              </a>
            ) : null}
          </span>
        </p>
      </>
    )}
  </CustomAnnouncementCard>
);

export default DiscussionAnnouncement;
