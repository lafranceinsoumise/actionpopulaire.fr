import { DateTime } from "luxon";
import React from "react";

import EventDescriptionCard from "./EventDescriptionCard";

export default {
  component: EventDescriptionCard,
  title: "Events/EventPage/EventDescriptionCard",
  parameters: {
    layout: "centered",
  },
};

const Template = (args) => <EventDescriptionCard {...args} />;

const futureDate = DateTime.fromISO("2045-01-01T00:00:00Z");

export const Default = Template.bind({});
Default.args = {
  illustration: {
    banner:
      "https://fakeimg.pl/350x200/?text=Événement%20ultime%20!&font=Poppins",
  },
  description: `
  <p>Réservez d’ores et déjà les dates dans vos agendas, ce sera <strong>un rendez-vous à ne pas manquer</strong>. L’événement politique de la rentrée se déroulera <strong>à Valence du 26 au 29 août 2021</strong>. Au programme : journées de formations, conférences et animations culturelles dans un cadre naturel et convivial.</p>
  <p><strong>Participez cet été à plusieurs jours d’échanges, de réflexions et de rencontres sur de nombreuses thématiques au sein d’un parc arboré, en pleine campagne drômoise</strong>. Le site du Palais des Congrès de Châteauneuf-sur-Isère comprend 6 000 m² totalement modulables avec un amphithéâtre de 967 places ainsi qu’un lac de 12 hectares. Le lieu propose des espaces de conférences et de détentes agréables tout en permettant le strict respect des règles sanitaires.</p>
  <p>Pour assister aux nombreuses conférences, débats et ateliers aux côtés d’intervenant·es reconnu·s et en provenance du monde entier, <strong><a href="https://actionpopulaire.fr/evenements/a19f007b-143f-4b7c-878f-9b480a1c7a3b/inscription/" title="Inscription AMFiS 2021">inscrivez-vous dès maintenant</a></strong> !</p>
  <p>➡️ <strong><a href="https://actionpopulaire.fr/formulaires/amfis-2021-volontaires/" title="Se porter volontaire">Je souhaite me proposer comme volontaire</a></strong></p>
  <p>➡️ <strong><a href="https://www.facebook.com/groups/2217166345081186" title="Hébergement solidaire">Je recherche / propose un hébergement solidaire</a></strong></p>
  <p>➡️ Je retrouve toutes les informations sur les AMFIS 2021 sur : <strong><a href="https://amfis2021.fr/">amfis2021.fr</a></strong></p>
  `,
  isOrganizer: false,
  endTime: futureDate,
  routes: {
    edit: "#eedit",
  },
};

export const DefaultWithNoImage = Template.bind({});
DefaultWithNoImage.args = {
  ...Default.args,
  illustration: null,
};

export const DefaultWithNoDescription = Template.bind({});
DefaultWithNoDescription.args = {
  ...Default.args,
  description: "",
};

export const OrganizerWithDescriptionAndImage = Template.bind({});
OrganizerWithDescriptionAndImage.args = {
  ...Default.args,
  isOrganizer: true,
};

export const OrganizerWithDescriptionAndNoImage = Template.bind({});
OrganizerWithDescriptionAndNoImage.args = {
  ...Default.args,
  isOrganizer: true,
  illustration: null,
};

export const OrganizerWithNoDescriptionAndNoImage = Template.bind({});
OrganizerWithNoDescriptionAndNoImage.args = {
  ...Default.args,
  isOrganizer: true,
  illustration: null,
  description: "",
};
