import { addQueryStringParams } from "@agir/lib/utils/url";

const ISE_URL =
  "https://www.service-public.fr/particuliers/vosdroits/demarches-et-outils/ISE";

export const getISELink = (data) => {
  const params = {};
  if (data?.lastName) {
    params.name = data.lastName;
  }
  if (data?.firstName) {
    params.firstNames = data.firstName;
  }
  if (data?.gender?.toLowerCase() === "f") {
    params.sexe = "feminin";
  }
  if (data?.gender?.toLowerCase() === "m") {
    params.sexe = "masculin";
  }
  if (data?.birthDate || data.dateOfBirth) {
    const date = (data.birthDate || data.dateOfBirth).split("-");
    params.birthYear = date[0];
    params.birthMonth = date[1];
    params.birthDay = date[2];
  }
  params.where =
    data?.votingLocation?.type === "consulate" ? "world" : "france";

  return addQueryStringParams(ISE_URL, params);
};

const FRENCH_EXT_LINK = "https://www.nosdeputes.fr/circonscription/rechercher/";
const ABROAD_EXT_LINK =
  "https://www.nosdeputes.fr/circonscription/departement/Fran%C3%A7ais+%C3%A9tablis+hors+de+France";

export const getCirconscriptionLegislativeSearchLink = (votingLocation) => {
  if (!votingLocation) {
    return FRENCH_EXT_LINK;
  }
  if (votingLocation.type === "consulate") {
    return ABROAD_EXT_LINK;
  }
  if (!votingLocation.departement) {
    return FRENCH_EXT_LINK;
  }
  return FRENCH_EXT_LINK + votingLocation.departement;
};
