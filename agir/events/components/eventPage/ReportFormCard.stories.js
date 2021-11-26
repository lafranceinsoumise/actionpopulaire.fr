import React from "react";

import { ReportFormCard } from "./ReportFormCard";

export default {
  component: ReportFormCard,
  title: "Events/EventPage/ReportFormCard",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <ReportFormCard {...args} />;

export const Default = Template.bind({});
Default.args = {
  title: "Comptabiliser nos efforts !",
  description:
    "Après avoir terminé votre porte-à-porte indiquez combien de portes vous avez toqué et de contacts avez-vous obtenu",
  url: "#formURL",
  submitted: false,
};

export const Submitted = Template.bind({});
Submitted.args = {
  ...Default.args,
  submitted: true,
};
