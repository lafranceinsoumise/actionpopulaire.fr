const MONTHS = [
  "janvier",
  "février",
  "mars",
  "avril",
  "mai",
  "juin",
  "juillet",
  "août",
  "septembre",
  "octobre",
  "novembre",
  "décembre"
];

const DAYS = [
  "dimanche",
  "lundi",
  "mardi",
  "mercredi",
  "jeudi",
  "vendredi",
  "samedi"
];

export function dateFromISOString(s) {
  return new Date(Date.parse(s));
}

export function displayHumanDate(date) {
  const now = new Date();
  const today = new Date(
    now.getFullYear(),
    now.getMonth(),
    now.getDate()
  ).valueOf();

  const days = (date.valueOf() - today) / 1000 / 3600 / 24;

  const time = `${date
    .getHours()
    .toString()
    .padStart(2, "0")}:${date
    .getMinutes()
    .toString()
    .padStart(2, "0")}`;
  const dayOfMonth =
    date.getDate() === 1 ? "1<sup>er</sup>" : date.getDate().toString();

  if (days < -360) {
    return `Le ${dayOfMonth} ${MONTHS[date.getMonth()]} ${date.getFullYear()}`;
  }

  if (days < -7) {
    return `Le ${dayOfMonth} ${MONTHS[date.getMonth()]} dernier`;
  }

  if (days < -1) {
    return `${DAYS[date.getDay()]} dernier à ${time}`;
  }

  if (days < 0) {
    return `Hier à ${time}`;
  }

  if (days < 1) {
    return `Aujourd'hui à ${time}`;
  }

  if (days < 8) {
    return `${DAYS[date.getDay()]} prochain à ${time}`;
  }

  if (days < 360) {
    return `Le ${dayOfMonth} ${MONTHS[date.getMonth()]} prochain`;
  }

  return `Le ${date.getDate()} ${
    MONTHS[date.getMonth()]
  } ${date.getFullYear()}`;
}
