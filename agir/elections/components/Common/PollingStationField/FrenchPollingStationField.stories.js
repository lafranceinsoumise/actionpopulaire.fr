import { http, HttpResponse } from "msw";
import React, { useState } from "react";

import FrenchPollingStationField from "./FrenchPollingStationField";
import TEST_DATA from "@agir/front/mockData/pollingStations";
import { getElectionEndpoint } from "./api";

export default {
  component: FrenchPollingStationField,
  title: "VotingProxies/FrenchPollingStationField",
  parameters: {
    layout: "padded",
    msw: {
      handlers: [
        http.get(getElectionEndpoint("searchVotingLocation"), ({ request }) => {
          const url = new URL(request.url);
          const search = url.searchParams.get("q");
          const results = TEST_DATA.filter((o) =>
            new RegExp(search, "gi").test(JSON.stringify(Object.values(o))),
          );
          return HttpResponse.json(results);
        }),
      ],
    },
  },
};

const Template = (args) => {
  const [value, setValue] = useState(args.value);
  return (
    <FrenchPollingStationField {...args} value={value} onChange={setValue} />
  );
};

export const Default = Template.bind({});
Default.args = {
  id: "location",
  name: "location",
  label: "Lieu",
  helpText: "Cherchez en commencant par un 'A'",
  error: "",
};
