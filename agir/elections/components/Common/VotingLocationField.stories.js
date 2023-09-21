import { rest } from "msw";
import React, { useState } from "react";

import VotingLocationField from "./VotingLocationField";
import TEST_DATA from "@agir/front/mockData/communesConsulats";
import { getElectionEndpoint } from "./api";

export default {
  component: VotingLocationField,
  title: "VotingProxies/VotingLocationField",
  parameters: {
    layout: "padded",
    msw: {
      handlers: [
        rest.get(
          getElectionEndpoint("searchVotingLocation"),
          (req, res, ctx) => {
            const search = req.url.searchParams.get("q");
            return res(
              ctx.json(
                TEST_DATA.filter((o) =>
                  new RegExp(search, "gi").test(
                    JSON.stringify(Object.values(o)),
                  ),
                ),
              ),
            );
          },
        ),
      ],
    },
  },
};

const Template = (args) => {
  const [value, setValue] = useState(args.value);
  return <VotingLocationField {...args} value={value} onChange={setValue} />;
};

export const Default = Template.bind({});
Default.args = {
  id: "location",
  name: "location",
  label: "Lieu",
  helpText: "Cherchez en commencant par un 'A'",
  error: "",
};
