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
  criteria: {
    genderBalance: true,
    activity: true,
    members: true,
    seasoned: true,
  },
};

export const Uncertifiable = Template.bind({});
Uncertifiable.args = {
  ...Certifiable.args,
  criteria: {
    genderBalance: false,
    activity: false,
    members: false,
    seasoned: false,
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
  criteria: {
    genderBalance: false,
    activity: true,
    members: true,
    seasoned: true,
    Boom: false,
  },
};
