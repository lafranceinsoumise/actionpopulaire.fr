import React from "react";

import GroupsPage from "./GroupsPage";
import { Container } from "@agir/front/genericComponents/grid";

export default {
  component: GroupsPage,
  title: "Groupes/GroupsPage",
};

const Template = (args) => (
  <Container style={{ minHeight: "100vh" }}>
    <GroupsPage {...args} />
  </Container>
);

export const Empty = Template.bind({});
Empty.args = {
  data: [],
};

export const Default = Template.bind({});
Default.args = {
  data: [
    {
      id: "90872185-3a66-4ab8-9405-1774edd483b8",
      name: "Clerc Jacquet SA",
      description:
        "Fin lit consulter fuir endormir. Absence consentir écouter autrefois blanc qui part. Amour officier saint nez.",
      type: "B",
      typeLabel: "Groupe thématique",
      url:
        "http://agir.local:8000/groupes/90872185-3a66-4ab8-9405-1774edd483b8/",
      eventCount: 1,
      membersCount: 15,
      isMember: true,
      isManager: true,
      labels: ["Groupe de rédaction du livret."],
      discountCodes: [],
      routes: {
        page:
          "http://agir.local:8000/groupes/90872185-3a66-4ab8-9405-1774edd483b8/",
        map:
          "http://agir.local:8000/carte/groupes/90872185-3a66-4ab8-9405-1774edd483b8/",
        calendar:
          "http://agir.local:8000/groupes/90872185-3a66-4ab8-9405-1774edd483b8/icalendar/",
        manage:
          "http://agir.local:8000/groupes/90872185-3a66-4ab8-9405-1774edd483b8/gestion/",
        edit:
          "http://agir.local:8000/groupes/90872185-3a66-4ab8-9405-1774edd483b8/gestion/modifier/",
        quit:
          "http://agir.local:8000/groupes/90872185-3a66-4ab8-9405-1774edd483b8/quitter/",
      },
    },
    {
      id: "46331667-6718-4e58-9c83-0ff958e17bb5",
      name: "Moulin Carlier SARL",
      description:
        "Ancien difficile par midi remplacer vague rejeter. Qui vieux autorité votre yeux aucun chat bête.",
      type: "L",
      typeLabel: "Groupe local",
      url:
        "http://agir.local:8000/groupes/46331667-6718-4e58-9c83-0ff958e17bb5/",
      eventCount: 0,
      membersCount: 7,
      isMember: true,
      isManager: false,
      labels: [],
      discountCodes: [],
      routes: {
        page:
          "http://agir.local:8000/groupes/46331667-6718-4e58-9c83-0ff958e17bb5/",
        map:
          "http://agir.local:8000/carte/groupes/46331667-6718-4e58-9c83-0ff958e17bb5/",
        calendar:
          "http://agir.local:8000/groupes/46331667-6718-4e58-9c83-0ff958e17bb5/icalendar/",
        manage:
          "http://agir.local:8000/groupes/46331667-6718-4e58-9c83-0ff958e17bb5/gestion/",
        edit:
          "http://agir.local:8000/groupes/46331667-6718-4e58-9c83-0ff958e17bb5/gestion/modifier/",
        quit:
          "http://agir.local:8000/groupes/46331667-6718-4e58-9c83-0ff958e17bb5/quitter/",
      },
    },
    {
      id: "09d80e5e-719a-4415-9f03-6d58fbedf183",
      name: "Diaz",
      description:
        "Mais impossible prix bout couche. Discussion ouvrir un tu usage observer.",
      type: "B",
      typeLabel: "Groupe thématique",
      url:
        "http://agir.local:8000/groupes/09d80e5e-719a-4415-9f03-6d58fbedf183/",
      eventCount: 0,
      membersCount: 1,
      isMember: true,
      isManager: false,
      labels: [],
      discountCodes: [],
      routes: {
        page:
          "http://agir.local:8000/groupes/09d80e5e-719a-4415-9f03-6d58fbedf183/",
        map:
          "http://agir.local:8000/carte/groupes/09d80e5e-719a-4415-9f03-6d58fbedf183/",
        calendar:
          "http://agir.local:8000/groupes/09d80e5e-719a-4415-9f03-6d58fbedf183/icalendar/",
        manage:
          "http://agir.local:8000/groupes/09d80e5e-719a-4415-9f03-6d58fbedf183/gestion/",
        edit:
          "http://agir.local:8000/groupes/09d80e5e-719a-4415-9f03-6d58fbedf183/gestion/modifier/",
        quit:
          "http://agir.local:8000/groupes/09d80e5e-719a-4415-9f03-6d58fbedf183/quitter/",
      },
    },
  ],
};

export const WithoutThematicGroups = Template.bind({});
WithoutThematicGroups.args = {
  data: Default.args.data.filter((group) => group.type !== "B"),
};
