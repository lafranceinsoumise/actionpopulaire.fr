import React from "react";

import GroupCertification from "./GroupCertification.js";

export default {
  component: GroupCertification,
  title: "GroupSettings/GroupCertification",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <GroupCertification {...args} />;

export const Certifiable = Template.bind({});
Certifiable.args = {
  certificationRequestURL:
    "https://lafranceinsoumise.fr/groupes-appui/demande-de-certification/",
  isCertified: false,
  certificationCriteria: {
    gender: { value: true, label: "Animation paritaire" },
    activity: {
      value: true,
      label:
        "Le groupe doit avoir organisé au moins trois événements dans les trois dernièrs mois d'un type très spécifique qui concerne les actions tournées vers l'extérieur et la société et non pas l'entre-soi des réunions internes de groupe.",
    },
    members: { value: true, label: "Nombre de membres" },
    creation: { value: true, label: "Date de création" },
  },
};

export const Uncertifiable = Template.bind({});
Uncertifiable.args = {
  ...Certifiable.args,
  certificationCriteria: {
    gender: { value: false, label: "Animation paritaire" },
    activity: { value: false, label: "Activité du groupe" },
    members: { value: false, label: "Nombre de membres" },
    creation: { value: false, label: "Date de création" },
  },
};

export const Certified = Template.bind({});
Certified.args = {
  ...Certifiable.args,
  isCertified: true,
};

export const CertifiedWithWarning = Template.bind({});
CertifiedWithWarning.args = {
  ...Certified.args,
  certificationCriteria: {
    gender: { value: false, label: "Animation paritaire" },
    activity: { value: true, label: "Activité du groupe" },
    members: { value: true, label: "Nombre de membres" },
    creation: { value: true, label: "Date de création" },
    Boom: { value: false },
  },
};
