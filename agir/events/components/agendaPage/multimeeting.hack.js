import { DateTime } from "luxon";

import illustration from "./MultiMeetingCard.webp";

export const MULTI_MEETING_CONFIG = {
  id: "hacked-ba0449a2-1734-47d0-a67f-8573c84d2623",
  name: "Multi-meeting Hologramme depuis Lille et 11 autres villes avec Jean-Luc Mélenchon le mardi 5 avril 2022",
  eventPageLink: "https://melenchon2022.fr/multi-meeting-hologramme/",
  illustration: { thumbnail: illustration, banner: illustration },
  startTime: "2022-04-05T19:30:00+02:00",
  endTime: "2022-04-05T21:00:00+02:00",
  timezone: "Europe/Paris",
  location: {
    name: "Lille Grand Palais",
    address1: "1 bd des Cités Unies",
    address2: "",
    zip: "59777",
    city: "Lille",
    country: "FR",
    address: "1 bd des Cités Unies\n59777 Lille",
    shortAddress: "1 bd des Cités Unies, 59777, Lille",
    shortLocation: "Lille Grand Palais (Lille)",
  },
};

export const checkHasMultiMeeting = () => {
  const today = DateTime.now();
  const multiMeetingDate = DateTime.fromISO(MULTI_MEETING_CONFIG.endTime);
  return today <= multiMeetingDate;
};

const getMultiMeeting = () =>
  checkHasMultiMeeting() ? MULTI_MEETING_CONFIG : null;

export default getMultiMeeting;
