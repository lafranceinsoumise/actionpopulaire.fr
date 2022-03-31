import { DateTime } from "luxon";

import illustration from "./MultiMeetingCard.webp";

export const MULTI_MEETING_CONFIG = {
  id: "hacked-ba0449a2-1734-47d0-a67f-8573c84d2623",
  name: "MULTI-MEETING HOLOGRAMME à Lille, Albertville, Besançon, Le Havre, Metz, Montluçon, Narbonne, Nice, Pau, Poitiers, Trappes, Vannes",
  eventPageLink: "https://melenchon2022.fr/multi-meeting-hologramme/",
  illustration: { thumbnail: illustration, banner: illustration },
  startTime: "2022-04-05T19:30:00+02:00",
  endTime: "2022-04-05T21:00:00+02:00",
  timezone: "Europe/Paris",
  location: {
    shortLocation: "À 2h de chez vous partout en France",
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
