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
    gender: true,
    activity: true,
    members: true,
    creation: true,
  },
};

export const Uncertifiable = Template.bind({});
Uncertifiable.args = {
  ...Certifiable.args,
  certificationCriteria: {
    gender: false,
    activity: false,
    members: false,
    creation: false,
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
    gender: false,
    activity: true,
    members: true,
    creation: true,
    Boom: false,
  },
};
