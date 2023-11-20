import { rest } from "msw";
import React from "react";

import ContributionRenewalPage from "./ContributionRenewalPage";
import TEST_DATA from "@agir/front/mockData/activeContribution";
import { getDonationEndpoint } from "../common/api";

const handlers = {
  submit: rest.post(getDonationEndpoint("createDonation"), (_, res, ctx) =>
    res(
      ctx.delay("real"),
      ctx.status(422),
      ctx.json({ global: "Une erreur est survenue !" }),
    ),
  ),
  monthly: rest.get(
    getDonationEndpoint("getActiveContribution"),
    (_, res, ctx) => res(ctx.delay("real"), ctx.json(TEST_DATA.monthly)),
  ),
  single: rest.get(
    getDonationEndpoint("getActiveContribution"),
    (_, res, ctx) => res(ctx.delay("real"), ctx.json(TEST_DATA.single)),
  ),
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
