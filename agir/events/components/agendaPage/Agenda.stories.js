import React from "react";

import Agenda from "./Agenda";
import { Container } from "@agir/front/genericComponents/grid";

export default {
  component: Agenda,
  title: "Dashboard/Agenda",
};

const Template = (args) => (
  <Container style={{ minHeight: "100vh" }}>
    <Agenda {...args} />
  </Container>
);

export const Empty = Template.bind({});
Empty.args = {
  rsvped: [],
  suggested: [],
};

export const Default = Template.bind({});
Default.args = {
  rsvped: [
    {
      id: "6d7684d9-8abf-45e8-b385-57a77fe63ba0",
      url:
        "http://agir.local:8000/evenements/6d7684d9-8abf-45e8-b385-57a77fe63ba0/",
      name: "Projet dessiner militaire appeler cause promettre peu.",
      hasSubscriptionForm: false,
      description: "",
      compteRendu: "",
      compteRenduPhotos: [],
      illustration: null,
      startTime: "2020-11-23T18:14:16.521246+01:00",
      endTime: "2020-11-23T21:14:16.521246+01:00",
      location: {
        name: "85, avenue de Marty",
        address1: "85, avenue de Marty",
        address2: "App. 6",
        zip: "71966",
        city: "Lemaitre",
        country: "FR",
        address: "85, avenue de Marty\nApp. 6\n71966 Lemaitre",
        shortAddress: "85, avenue de Marty, App. 6, 71966, Lemaitre",
        shortLocation: "85, avenue de Marty (Lemaitre)",
        coordinates: {
          type: "Point",
          coordinates: [48.86667, 2.08333],
        },
      },
      isOrganizer: false,
      rsvp: "CO",
      participantCount: 11,
      options: {
        price: null,
      },
      routes: {
        details:
          "http://agir.local:8000/evenements/6d7684d9-8abf-45e8-b385-57a77fe63ba0/",
        map:
          "http://agir.local:8000/carte/evenements/6d7684d9-8abf-45e8-b385-57a77fe63ba0/",
        join:
          "http://agir.local:8000/evenements/6d7684d9-8abf-45e8-b385-57a77fe63ba0/inscription/",
        cancel:
          "http://agir.local:8000/evenements/6d7684d9-8abf-45e8-b385-57a77fe63ba0/quitter/",
        manage:
          "http://agir.local:8000/evenements/6d7684d9-8abf-45e8-b385-57a77fe63ba0/manage/",
        calendarExport:
          "http://agir.local:8000/evenements/6d7684d9-8abf-45e8-b385-57a77fe63ba0/icalendar/",
        compteRendu:
          "http://agir.local:8000/evenements/6d7684d9-8abf-45e8-b385-57a77fe63ba0/compte-rendu/",
        addPhoto:
          "http://agir.local:8000/evenements/6d7684d9-8abf-45e8-b385-57a77fe63ba0/importer-image/",
        edit:
          "http://agir.local:8000/evenements/6d7684d9-8abf-45e8-b385-57a77fe63ba0/modifier/",
        googleExport:
          "https://calendar.google.com/calendar/r/eventedit?text=Projet…5%2C+avenue+de+Marty%2C+App.+6%2C+71966%2C+Lemaitre&details=",
      },
      groups: [
        {
          id: "9389e3d6-34f2-4f3a-9dcb-73d8d262b46f",
          name: "Groupe d'action du Café de la Gare",
          description: "",
          type: "L",
          typeLabel: "Groupe local",
          url:
            "http://agir.local:8000/groupes/9389e3d6-34f2-4f3a-9dcb-73d8d262b46f/",
          eventCount: 3,
          membersCount: 2,
          isMember: true,
          isManager: true,
          labels: [],
          discountCodes: [],
          routes: {
            page:
              "http://agir.local:8000/groupes/9389e3d6-34f2-4f3a-9dcb-73d8d262b46f/",
            map:
              "http://agir.local:8000/carte/groupes/9389e3d6-34f2-4f3a-9dcb-73d8d262b46f/",
            calendar:
              "http://agir.local:8000/groupes/9389e3d6-34f2-4f3a-9dcb-73d8d262b46f/icalendar/",
            manage:
              "http://agir.local:8000/groupes/9389e3d6-34f2-4f3a-9dcb-73d8d262b46f/gestion/",
            edit:
              "http://agir.local:8000/groupes/9389e3d6-34f2-4f3a-9dcb-73d8d262b46f/gestion/modifier/",
            quit:
              "http://agir.local:8000/groupes/9389e3d6-34f2-4f3a-9dcb-73d8d262b46f/quitter/",
          },
        },
      ],
      contact: null,
    },
  ],
  suggested: [
    {
      id: "e419f6e8-7431-43c9-ae9a-b82362a6bc81",
      url:
        "http://agir.local:8000/evenements/e419f6e8-7431-43c9-ae9a-b82362a6bc81/",
      name: "Consulter moitié inspirer se taire.",
      hasSubscriptionForm: false,
      description: "",
      compteRendu: "",
      compteRenduPhotos: [],
      illustration: null,
      startTime: "2020-12-02T18:14:16.979107+01:00",
      endTime: "2020-12-02T21:14:16.979107+01:00",
      location: {
        name: "54, chemin de Lejeune",
        address1: "54, chemin de Lejeune",
        address2: "App. 36",
        zip: "02376",
        city: "Saint Alain",
        country: "FR",
        address: "54, chemin de Lejeune\nApp. 36\n02376 Saint Alain",
        shortAddress: "54, chemin de Lejeune, App. 36, 02376, Saint Alain",
        shortLocation: "54, chemin de Lejeune (Saint Alain)",
        coordinates: {
          type: "Point",
          coordinates: [43.32393, 5.4584],
        },
      },
      isOrganizer: false,
      rsvp: null,
      participantCount: 9,
      options: {
        price: null,
      },
      routes: {
        details:
          "http://agir.local:8000/evenements/e419f6e8-7431-43c9-ae9a-b82362a6bc81/",
        map:
          "http://agir.local:8000/carte/evenements/e419f6e8-7431-43c9-ae9a-b82362a6bc81/",
        join:
          "http://agir.local:8000/evenements/e419f6e8-7431-43c9-ae9a-b82362a6bc81/inscription/",
        cancel:
          "http://agir.local:8000/evenements/e419f6e8-7431-43c9-ae9a-b82362a6bc81/quitter/",
        manage:
          "http://agir.local:8000/evenements/e419f6e8-7431-43c9-ae9a-b82362a6bc81/manage/",
        calendarExport:
          "http://agir.local:8000/evenements/e419f6e8-7431-43c9-ae9a-b82362a6bc81/icalendar/",
        compteRendu:
          "http://agir.local:8000/evenements/e419f6e8-7431-43c9-ae9a-b82362a6bc81/compte-rendu/",
        addPhoto:
          "http://agir.local:8000/evenements/e419f6e8-7431-43c9-ae9a-b82362a6bc81/importer-image/",
        edit:
          "http://agir.local:8000/evenements/e419f6e8-7431-43c9-ae9a-b82362a6bc81/modifier/",
        googleExport:
          "https://calendar.google.com/calendar/r/eventedit?text=Consul…hemin+de+Lejeune%2C+App.+36%2C+02376%2C+Saint+Alain&details=",
      },
      groups: [
        {
          id: "9389e3d6-34f2-4f3a-9dcb-73d8d262b46f",
          name: "Groupe d'action du Café de la Gare",
          description: "",
          type: "L",
          typeLabel: "Groupe local",
          url:
            "http://agir.local:8000/groupes/9389e3d6-34f2-4f3a-9dcb-73d8d262b46f/",
          eventCount: 3,
          membersCount: 2,
          isMember: true,
          isManager: true,
          labels: [],
          discountCodes: [],
          routes: {
            page:
              "http://agir.local:8000/groupes/9389e3d6-34f2-4f3a-9dcb-73d8d262b46f/",
            map:
              "http://agir.local:8000/carte/groupes/9389e3d6-34f2-4f3a-9dcb-73d8d262b46f/",
            calendar:
              "http://agir.local:8000/groupes/9389e3d6-34f2-4f3a-9dcb-73d8d262b46f/icalendar/",
            manage:
              "http://agir.local:8000/groupes/9389e3d6-34f2-4f3a-9dcb-73d8d262b46f/gestion/",
            edit:
              "http://agir.local:8000/groupes/9389e3d6-34f2-4f3a-9dcb-73d8d262b46f/gestion/modifier/",
            quit:
              "http://agir.local:8000/groupes/9389e3d6-34f2-4f3a-9dcb-73d8d262b46f/quitter/",
          },
        },
      ],
      contact: null,
    },
  ],
};
