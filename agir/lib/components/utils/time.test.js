import { DateTime, Interval } from "luxon";

import { displayHumanDate, displayInterval } from "./time";

const date = (s) =>
  DateTime.fromFormat(s, "d/M H:mm", { zone: "Europe/Paris" })
    .set({ year: 2021 })
    .setLocale("fr-FR");

test("displayDate des dates relatives pour des dates proches", () => {
  const relativeTo = date("20/3 12:00"); // Samedi 20 mars 2021, 12:00

  expect(displayHumanDate(date("21/3 10:30"), relativeTo)).toEqual(
    "demain à 10:30",
  );

  expect(displayHumanDate(date("22/3 16:14"), relativeTo)).toEqual(
    "après-demain à 16:14",
  );

  expect(displayHumanDate(date("20/3 12:30"), relativeTo)).toEqual(
    "aujourd’hui à 12:30",
  );

  expect(displayHumanDate(date("19/3 9:30"), relativeTo)).toEqual(
    "hier à 9:30",
  );

  expect(displayHumanDate(date("18/3 23:59"), relativeTo)).toEqual(
    "avant-hier à 23:59",
  );
});

test("displayDate utilise le jour de la semaine pour une date proche", () => {
  const relativeTo = date("20/3 12:00"); // Samedi 20 mars 2021, 12:00

  // LIMITES INFERIEURES
  expect(displayHumanDate(date("23/3 08:01"), relativeTo)).toEqual(
    "mardi prochain à 8:01",
  );

  expect(displayHumanDate(date("17/3 13:01"), relativeTo)).toEqual(
    "mercredi dernier à 13:01",
  );

  // LIMITES SUPERIEURES
  // les deux jours limites, en prenant des jours écartés de plus de 24 * 7 heures
  expect(displayHumanDate(date("27/3 13:01"), relativeTo)).toEqual(
    "samedi prochain à 13:01",
  );
  expect(displayHumanDate(date("13/3 11:32"), relativeTo)).toEqual(
    "samedi dernier à 11:32",
  );
});

test("displayDate renvoie une date complète pour une date plus lointaine", () => {
  const relativeTo = date("20/3 12:00"); // Samedi 20 mars 2021, 12:00

  expect(displayHumanDate(date("28/3 08:01"), relativeTo)).toEqual(
    "dimanche 28 mars à 8:01",
  );

  expect(displayHumanDate(date("12/3 13:01"), relativeTo)).toEqual(
    "vendredi 12 mars à 13:01",
  );

  expect(displayHumanDate(date("30/12 10:12"), relativeTo)).toEqual(
    "30 décembre 2021 à 10:12",
  );
});

test("displayInterval renvoie des valeurs correctes pour deux horaires le même jour", () => {
  const relativeTo = date("20/3 12:00"); // Samedi 20 mars 2021, 12:00

  expect(
    displayInterval(
      Interval.fromDateTimes(date("21/3 10:00"), date("21/3 12:00")),
      relativeTo,
    ),
  ).toEqual("le dimanche 21 mars, de 10:00 à 12:00");

  expect(
    displayInterval(
      Interval.fromDateTimes(date("21/9 19:00"), date("22/9 12:00")),
      relativeTo,
    ),
  ).toEqual(
    "du mardi 21 septembre 2021 à 19:00 au mercredi 22 septembre à 12:00",
  );
});

test("displayHumanDate n'a pas de problème quand on franchit la fin d'un mois", () => {
  expect(displayHumanDate(date("01/07 20:00"), date("29/06 20:00"))).toEqual(
    "après-demain à 20:00",
  );
});

test("displayHumanDate gère correctement les cas ambigus", () => {
  const relativeTo = date("17/3 12:00"); // Mercredi 17 mars 2021

  expect(displayHumanDate(date("20/3 12:00"), relativeTo)).toEqual(
    "samedi à 12:00",
  );

  expect(displayHumanDate(date("23/3 12:00"), relativeTo)).toEqual(
    "mardi prochain à 12:00",
  );

  expect(displayHumanDate(date("14/3 12:00"), relativeTo)).toEqual(
    "dimanche dernier à 12:00",
  );
});
