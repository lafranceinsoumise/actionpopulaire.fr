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
  routes: [
    {
      id: "certification",
      getLink: () => "/certificationPanelRoute",
    },
  ],
  isCertifiable: true,
  isCertified: false,
  certificationCriteria: {
    gender: { value: true },
    activity: { value: true },
    members: { value: true },
    creation: { value: true },
  },
};

export const Uncertifiable = Template.bind({});
Uncertifiable.args = {
  ...Certifiable.args,
  isCertifiable: true,
  certificationCriteria: {
    gender: { value: true },
    activity: { value: false },
    members: { value: true },
    creation: { value: true },
  },
};

export const Certified = Template.bind({});
Certified.args = {
  ...Certifiable.args,
  isCertifiable: true,
  isCertified: true,
};

export const CertifiedWithWarning = Template.bind({});
CertifiedWithWarning.args = {
  ...Certified.args,
  isCertifiable: true,
  certificationCriteria: {
    gender: { value: false },
    activity: { value: true },
    members: { value: true },
    creation: { value: true },
  },
};
