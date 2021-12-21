import React from "react";

import OnlineUrlCard from "./OnlineUrlCard";

export default {
  component: OnlineUrlCard,
  title: "Events/EventPage/OnlineUrlCard",
  parameters: {
    layout: "padded",
  },
};

const Template = (args) => <OnlineUrlCard {...args} />;

export const Default = Template.bind({});
Default.args = {
  onlineUrl:
    "https://www.figma.com/file/29dCZ0UujALl47UIEnecqp/Bouton-rejoindre-en-ligne?node-id=2%3A3168",
};

export const Youtube = Template.bind({});
Youtube.args = {
  youtubeVideoID: "ZZ5LpwO-An4",
};
