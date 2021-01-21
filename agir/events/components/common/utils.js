import { DateTime, Interval } from "luxon";

export const formatEvent = (event) => {
  if (!event) {
    return null;
  }

  if (!event.startTime || !event.endTime) {
    return event;
  }

  try {
    const startDateTime = DateTime.fromJSDate(
      new Date(event.startTime)
    ).setLocale("fr");
    const endDateTime = DateTime.fromJSDate(new Date(event.endTime)).setLocale(
      "fr"
    );
    return {
      ...event,
      schedule: Interval.fromDateTimes(startDateTime, endDateTime),
    };
  } catch (e) {
    return event;
  }
};
