import React from "react";

import CertificationStatus from "./CertificationStatus.js";

export default {
  component: CertificationStatus,
  title: "GroupSettings/CertificationStatus",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <CertificationStatus {...args} />;

export const Certifiable = Template.bind({});
Certifiable.args = {
  routes: {
    certificationRequest: "/certificationPanelRoute",
  },
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
    gender: true,
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
