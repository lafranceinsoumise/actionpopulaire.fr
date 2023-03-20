import PropTypes from "prop-types";
import React from "react";
import useSWR from "swr";

import AnnouncementCard from "./AnnouncementCard";
import GenericCard from "./GenericCard";
import GroupMembershipLimitReminderCard from "./GroupMembershipLimitReminderCard";
import ReferralUpdateCard from "./ReferralUpdateCard";

import CONFIG from "@agir/activity/common/activity.config";
import { getEventEndpoint } from "@agir/events/common/api";

export const ActivityCard = (props) => {
  const { type, announcement } = props;
  const config = type && CONFIG[type];

  if (!config) {
    return null;
  }

  if (type === "announcement" && announcement) {
    return <AnnouncementCard {...announcement} config={config} />;
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

const ConnectedActivityCard = (props) => {
  const { type } = props;
  const config = type && CONFIG[type];
  const hasEventCard = config?.hasEvent && props.event;
  const { data: eventDetails } = useSWR(
    hasEventCard &&
      getEventEndpoint("getEventCard", { eventPk: props.event.id }),
    {
      revalidateIfStale: false,
      revalidateOnFocus: false,
      revalidateOnReconnect: false,
    }
  );

  return config ? (
    <ActivityCard
      {...props}
      config={config}
      event={eventDetails || props.event}
      isLoadingEventCard={hasEventCard && typeof eventDetails === "undefined"}
    />
  ) : null;
};
ConnectedActivityCard.propTypes = {
  type: PropTypes.oneOf(Object.keys(CONFIG)),
  event: PropTypes.object,
};

export default ConnectedActivityCard;
