import { http, HttpResponse, delay } from "msw";
import React, { useState } from "react";

import CommuneField from "./CommuneField";
import TEST_DATA from "@agir/front/mockData/communes";

export default {
  component: CommuneField,
  title: "Form/CommuneField",
  parameters: {
    layout: "padded",
    msw: {
      handlers: [
        http.get("/data-france/communes/chercher/", ({ request }) => {
          const url = new URL(request.url);
          const search = url.searchParams.get("q");
          const results = TEST_DATA.results.filter((o) =>
            new RegExp(search, "gi").test(JSON.stringify(Object.values(o))),
          );
          delay("real");
          return HttpResponse.json({ results });
        }),
      ],
    },
  },
};

const Template = (args) => {
  const [value, setValue] = useState(args.value);
  return (
    <div
      style={{
        boxSizing: "border-box",
        padding: "32px 16px",
        maxWidth: "480px",
        margin: "0 auto",
      }}
    >
      <CommuneField {...args} value={value} onChange={setValue} />
      <pre>
        Value :{" "}
        {value ? (
          <strong>{JSON.stringify(value, null, "  ")}</strong>
        ) : (
          <em>empty</em>
        )}
      </pre>
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  id: "commune",
  name: "commune",
  label: "Commune",
  helpText: "Cherchez en commencant par un 'A' ou par '6'",
  error: "",
  types: ["COM", "ARM"],
};
