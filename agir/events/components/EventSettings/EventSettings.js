import React from "react";

import ObjectManagement from "@agir/front/genericComponents/ObjectManagement";

import events from "@agir/front/mockData/events.json";

const MENU_ITEMS_EVENTS = {
  information: {
    id: "information",
    label: "Général",
    icon: "file-text",
  },
  participants: {
    id: "participants",
    label: "Participant·es",
    labelFunction: (object) =>
      `${(object && object.participantCount) || ""} Participant·es`.trim(),
    icon: "users",
  },
  organizerGroups: {
    id: "organizerGroups",
    label: "Co-organisation",
    icon: "settings",
  },
  rights: {
    id: "rights",
    label: "Droits",
    icon: "lock",
  },
  onlineMeeting: {
    id: "onlineMeeting",
    label: "Vidéoconférence",
    icon: "video",
  },
  contact: {
    id: "contact",
    label: "Contact",
    icon: "mail",
  },
  location: {
    id: "location",
    label: "Localisation",
    icon: "map-pin",
  },
  report: {
    id: "report",
    label: "Compte-rendu",
    disabledLabel: "À remplir à la fin de l’événement",
    disabled: true,
    icon: "image",
  },
};

export const EventSettings = () => {
  return <ObjectManagement object={events[0]} menu_items={MENU_ITEMS_EVENTS} />;
};
EventSettings.propTypes = {};

export default EventSettings;
