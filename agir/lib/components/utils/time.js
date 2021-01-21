import { DateTime, Interval } from "luxon";
import { instanceOf } from "prop-types";

const HOUR_ONLY_FORMAT = {
  hour: "numeric",
  minute: "2-digit",
};

const SAME_YEAR_FORMAT = {
  weekday: "long",
  month: "long",
  day: "numeric",
  hour: "numeric",
  minute: "2-digit",
};

const OTHER_YEAR_FORMAT = {
  year: "numeric",
  month: "long",
  day: "numeric",
  hour: "numeric",
  minute: "2-digit",
};

export function dateFromISOString(s) {
  return DateTime.fromISO(s).setLocale("fr");
}

export function displayHumanDay(datetime, relativeTo, interval) {
  if (!instanceOf(datetime, DateTime)) {
    return datetime;
  }

  if (relativeTo === undefined) {
    relativeTo = DateTime.local();
  }

  if (interval === undefined) {
    interval =
      relativeTo < datetime
        ? Interval.fromDateTimes(relativeTo, datetime)
        : Interval.fromDateTimes(datetime, relativeTo);
  }

  const calendarDays = interval.count("days");

  if (calendarDays <= 3) {
    return datetime.toRelativeCalendar({
      base: relativeTo,
      unit: "days",
    });
  } else if (calendarDays <= 8) {
    const calendarWeeks = interval.count("weeks");
    const qualifier =
      relativeTo < datetime ? (calendarWeeks > 1 ? "prochain" : "") : "dernier";
    return `${datetime.weekdayLong} ${qualifier}`.trim();
  }

  const format = {
    weekday: "long",
    month: "long",
    day: "numeric",
    year: datetime < relativeTo ? "numeric" : undefined,
  };

  return datetime.toLocaleString(format);
}

export function displayHumanDate(datetime, relativeTo) {
  if (!instanceOf(datetime, DateTime)) {
    return datetime;
  }

  if (relativeTo === undefined) {
    relativeTo = DateTime.local();
  }
  const interval =
    relativeTo < datetime
      ? Interval.fromDateTimes(relativeTo, datetime)
      : Interval.fromDateTimes(datetime, relativeTo);

  const calendarDays = interval.count("days");

  if (calendarDays <= 8) {
    return `${displayHumanDay(
      datetime,
      relativeTo,
      interval
    )} à ${datetime.toLocaleString(HOUR_ONLY_FORMAT)}`;
  } else if (interval.count("months") <= 4) {
    return datetime.toLocaleString(SAME_YEAR_FORMAT);
  } else {
    return datetime.toLocaleString(OTHER_YEAR_FORMAT);
  }
}

export const displayHumanDateString = (datetime, relativeTo) => {
  datetime = new Date(datetime);
  datetime = DateTime.fromJSDate(datetime);

  if (relativeTo) {
    relativeTo = new Date(relativeTo);
    relativeTo = DateTime.fromJSDate(relativeTo);
  }

  return displayHumanDate(datetime, relativeTo);
};

export function displayInterval(interval, relativeTo) {
  if (relativeTo === undefined) {
    relativeTo = DateTime.local().setLocale("fr");
  }

  const fromNowInterval =
    relativeTo < interval.start
      ? Interval.fromDateTimes(relativeTo, interval.start)
      : Interval.fromDateTimes(interval.start, relativeTo);

  const showYear = fromNowInterval.count("months") > 4;
  const scheduleCalendarDays = interval.count("days");

  const dayPartFormat = {
    year: showYear ? "numeric" : undefined,
    month: "long",
    day: "numeric",
  };

  if (scheduleCalendarDays === 1) {
    const dayPart = interval.start.toLocaleString(dayPartFormat);
    const hourPart = `de ${interval.start.toLocaleString(
      HOUR_ONLY_FORMAT
    )} à ${interval.end.toLocaleString(HOUR_ONLY_FORMAT)}`;
    return `le ${dayPart}, ${hourPart}`;
  }

  const start = interval.start.toLocaleString({
    ...dayPartFormat,
    ...HOUR_ONLY_FORMAT,
  });
  const end = interval.end.toLocaleString({
    ...dayPartFormat,
    ...HOUR_ONLY_FORMAT,
    year: undefined,
  });
  return `du ${start} au ${end}`;
}

export function displayIntervalStart(interval, relativeTo) {
  if (relativeTo === undefined) {
    relativeTo = DateTime.local().setLocale("fr");
  }
  const startDate = interval.start.setLocale("fr-FR");
  const endDate = interval.end.setLocale("fr-FR");

  const scheduleCalendarDays = interval.count("days");

  const dayPartFormat = {
    year: endDate < relativeTo ? "numeric" : undefined,
    month: "long",
    day: "numeric",
  };

  if (scheduleCalendarDays === 1) {
    const dayPart = startDate.toLocaleString(dayPartFormat);
    const hourPart = `${startDate.toLocaleString(HOUR_ONLY_FORMAT)}`;

    return `${dayPart}, ${hourPart}`;
  }

  const start = startDate.toLocaleString({
    ...dayPartFormat,
    ...HOUR_ONLY_FORMAT,
  });

  return `${start}`;
}

const units = ["year", "month", "week", "day", "hour", "minute", "second"];

export const timeAgo = (date) => {
  try {
    let dateTime = new Date(date);
    dateTime = DateTime.fromJSDate(dateTime);
    const diff = dateTime.diffNow().shiftTo(...units);
    const unit = units.find((unit) => diff.get(unit) !== 0) || "second";
    const relativeFormatter = new Intl.RelativeTimeFormat("fr", {
      numeric: "auto",
    });
    return relativeFormatter.format(Math.trunc(diff.as(unit)), unit);
  } catch (e) {
    return date;
  }
};

export const displayShortDate = (datetime) => {
  try {
    let date = new Date(datetime);
    date = DateTime.fromJSDate(date).setLocale("fr");
    return date.toFormat("dd/LL");
  } catch (e) {
    return datetime;
  }
};
