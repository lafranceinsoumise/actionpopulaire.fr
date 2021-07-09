import React from "react";

import SentDocumentsCard from "./SentDocumentsCard";

export default {
  component: SentDocumentsCard,
  title: "Event Required Documents/SentDocumentsCard",
};

const Template = (args) => (
  <div style={{ maxWidth: 372, width: "100%", margin: "10px auto" }}>
    <SentDocumentsCard {...args} />
  </div>
);

export const Default = Template.bind({});
Default.args = {
  documents: [
    {
      id: "a",
      type: "ABC",
      name: "Prêt de retro-projecteur",
      link: "#docABC",
    },
    {
      id: "b",
      type: "CBA",
      name: "Attestation de règlement des consommations",
      link: "#docCBA",
    },
  ],
};
