import React from "react";

import CampaignFundingField from "./CampaignFundingField";

export default {
  component: CampaignFundingField,
  title: "EventForm/CampaignFundingField",
  parameters: {
    layout: "centered",
  },
};

const Template = (args) => {
  return <CampaignFundingField {...args} />;
};

export const Private = Template.bind({});
Private.args = {
  isPrivate: true,
};
export const CertifiedWithDocs = Template.bind({});
CertifiedWithDocs.args = {
  isCertified: true,
  needsDocuments: true,
  groupPk: "755e460f-9cf1-499e-952a-522fa8629852",
};
export const CertifiedWithoutDocs = Template.bind({});
CertifiedWithoutDocs.args = {
  isCertified: true,
  needsDocuments: false,
  groupPk: "755e460f-9cf1-499e-952a-522fa8629852",
};
export const UncertifiedWithDocs = Template.bind({});
UncertifiedWithDocs.args = {
  isCertified: false,
  needsDocuments: true,
  groupPk: "755e460f-9cf1-499e-952a-522fa8629852",
};
export const UncertifiedWithoutDocs = Template.bind({});
UncertifiedWithoutDocs.args = {
  isCertified: false,
  needsDocuments: false,
  groupPk: "755e460f-9cf1-499e-952a-522fa8629852",
};
export const WithError = Template.bind({});
WithError.args = {
  isCertified: true,
  needsDocuments: true,
  groupPk: "755e460f-9cf1-499e-952a-522fa8629852",
  error: "Aïe aïe aïe",
};
