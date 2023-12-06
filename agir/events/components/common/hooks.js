import { Interval } from "luxon";
import { useMemo } from "react";
import useSWR from "swr";

import { dateFromISOString, displayHumanDay } from "@agir/lib/utils/time";
import { getEventEndpoint } from "./api";

export const useEventFormOptions = () => {
  const { data: eventOptions } = useSWR(
    getEventEndpoint("eventPropertyOptions"),
  );

  const organizerGroup = useMemo(() => {
    if (eventOptions && Array.isArray(eventOptions.organizerGroup)) {
      return [
        ...eventOptions.organizerGroup.map((group) => ({
          ...group,
          label: group.name,
          value: group.id,
        })),
        {
          id: null,
          value: null,
          label: "À titre individuel",
          contact: eventOptions.defaultContact,
        },
      ];
    }
  }, [eventOptions]);

  return eventOptions
    ? {
        ...eventOptions,
        organizerGroup,
      }
    : {};
};

export const useEventsByDay = (events, dayFormatFn = displayHumanDay) => {
  const byDay = useMemo(
    () =>
      Array.isArray(events)
        ? events.reduce((days, event) => {
            const day = dayFormatFn(dateFromISOString(event.startTime));
            (days[day] = days[day] || []).push({
              ...event,
              schedule: Interval.fromDateTimes(
                dateFromISOString(event.startTime),
                dateFromISOString(event.endTime),
              ),
            });
            return days;
          }, {})
        : undefined,
    [events],
  );

  return byDay;
};
