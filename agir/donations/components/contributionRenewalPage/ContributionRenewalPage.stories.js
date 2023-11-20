import { http, HttpResponse, delay } from "msw";
import React from "react";

import ContributionRenewalPage from "./ContributionRenewalPage";
import TEST_DATA from "@agir/front/mockData/activeContribution";
import { getDonationEndpoint } from "../common/api";

const handlers = {
  submit: http.post(getDonationEndpoint("createDonation"), () => {
    delay("real");
    return HttpResponse.json(
      {
        global: "Une erreur est survenue !",
      },
      { status: 422 },
    );
  }),
  monthly: http.get(getDonationEndpoint("getActiveContribution"), () => {
    delay("real");
    return HttpResponse.json(TEST_DATA.monthly);
  }),
  single: http.get(getDonationEndpoint("getActiveContribution"), () => {
    delay("real");
    return HttpResponse.json(TEST_DATA.single);
  }),
};

export default {
  component: ContributionRenewalPage,
  title: "Donations/Contributions/ContributionRenewalPage",
};

const Template = (args) => <ContributionRenewalPage {...args} />;

export const Monthly = Template.bind({});
Monthly.args = {};
Monthly.parameters = {
  msw: {
    handlers: [handlers.monthly, handlers.submit],
  },
};

export const SingleTime = Template.bind({});
SingleTime.args = {};
SingleTime.parameters = {
  msw: {
    handlers: [handlers.single, handlers.submit],
  },
};
