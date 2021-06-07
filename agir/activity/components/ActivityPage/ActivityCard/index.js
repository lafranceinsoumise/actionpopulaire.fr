import PropTypes from "prop-types";
import React from "react";

import AnnouncementCard from "./AnnouncementCard";
import GenericCard from "./GenericCard";
import GroupMembershipLimitReminderCard from "./GroupMembershipLimitReminderCard";
import ReferralUpdateCard from "./ReferralUpdateCard";

import CONFIG from "@agir/activity/common/activity.config";

const ActivityCard = (props) => {
  const { type } = props;

  if (!type || !CONFIG[type]) {
    return null;
  }

  const config = CONFIG[type];

  if (type === "announcement" && props?.announcement) {
    return <AnnouncementCard {...props.announcement} config={config} />;
  }

  if (type === "referral-accepted") {
    return <ReferralUpdateCard {...props} config={config} />;
  }

  if (type === "group-membership-limit-reminder") {
    return <GroupMembershipLimitReminderCard {...props} config={config} />;
  }

  return <GenericCard {...props} config={config} />;
};
ActivityCard.propTypes = {
  type: PropTypes.oneOf(Object.keys(CONFIG)),
  announcement: PropTypes.object,
};

export default ActivityCard;
