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
  certificationPanelRoute: "/certificationPanelRoute",
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
    genderBalance: true,
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
