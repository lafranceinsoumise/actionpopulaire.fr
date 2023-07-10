import { DateTime } from "luxon";
import React from "react";

import CONFIG from "@agir/activity/common/activity.config";
import { ACTIVITY_STATUS } from "@agir/activity/common/helpers";
import group from "@agir/front/mockData/group";
import events from "@agir/front/mockData/events";

import { ActivityCard } from "./index";

import { decorateArgs, reorganize } from "@agir/lib/utils/storyUtils";

const event = events[0];

export default {
  component: ActivityCard,
  title: "Activities/ActivityCard",
  parameters: {
    layout: "centered",
  },
  argTypes: {
    type: {
      name: "Type de carte",
      control: {
        type: "select",
        options: Object.keys(CONFIG),
      },
    },
    event: {
      control: { type: "object" },
    },
    group: {
      control: { type: "object" },
    },
    meta: {
      control: { type: "object" },
    },
    announcement: {
      control: { type: "object" },
    },
    isLoadingEventCard: {
      control: { type: "boolean" },
    },
  },
};

/**
 * Convertit startTime/duration fourni par les contrôles dans le format attendu
 * par le composant : startTime et endTime, au format ISO tous les deux.
 */
const convertDatetimes = ({
  event: { startTime, duration, ...event },
  ...args
}) => {
  let start = new Date(startTime);
  start = DateTime.fromJSDate(start);
  return {
    ...args,
    event: {
      ...event,
      startTime: start.toISO(),
      endTime: start.plus({ hours: duration }).toISO(),
    },
  };
};

const ActivityCardStory = (props) => <ActivityCard {...props} />;

const Template = decorateArgs(
  convertDatetimes,
  reorganize(
    {
      "event.location": {
        name: "event.locationName",
        address: "event.locationAddress",
        shortAddress: "event.shortAddress",
      },
    },
    true
  ),
  ActivityCardStory
);

export const Default = Template.bind({});
Default.args = {
  id: 1,
  type: "announcement",
  event,
  group: group,
  status: ACTIVITY_STATUS.STATUS_DISPLAYED,
  individual: {
    displayName: "Clara",
    email: "clara@example.com",
  },
  timestamp: DateTime.local().minus({ hours: 5 }).toISO(),
  meta: {
    totalReferrals: 10,
    oldGroup: "An old group",
    transferredMemberships: 1000,
    membershipLimit: 50,
    membershipCount: 5,
    membershipLimitNotificationStep: 1,
  },
  routes: {
    createEvent: "#createEvent",
    createGroup: "#createGroup",
    newGroupHelp: "#newGroupHelp",
  },
  announcement: {
    id: "4ffb6d51-df76-4621-a933-7679edfced91",
    title: "16 mai : Meeting de Jean-Luc Mélenchon",
    link: "http://agir.local:8000/activite/4ffb6d51-df76-4621-a933-7679edfced91/lien/",
    content:
      "<p>Réservez votre après-midi pour le premier meeting en plein air à la campagne #MeetingAubin</p>",
    image: {
      desktop: "https://loremflickr.com/255/130",
      mobile: "https://loremflickr.com/160/160",
      activity: "https://loremflickr.com/548/241",
    },
    startDate: "2021-05-17T17:33:46+02:00",
    endDate: null,
    priority: 0,
    activityId: 1341,
    customDisplay: "",
    status: ACTIVITY_STATUS.STATUS_DISPLAYED,
  },
  isLoadingEventCard: false,
};

export const Interacted = Template.bind({});
Interacted.args = {
  ...Default.args,
  status: ACTIVITY_STATUS.STATUS_INTERACTED,
  announcement: {
    ...Default.args.announcement,
    status: ACTIVITY_STATUS.STATUS_INTERACTED,
  },
};
