import React from "react";

import EventFacebookLinkCard from "./EventFacebookLinkCard";

export default {
  component: EventFacebookLinkCard,
  title: "Events/EventPage/FacebookLink",
};

const Template = (args) => <EventFacebookLinkCard {...args} />;

export const Default = Template.bind({});
Default.args = {
  routes: { facebook: "https://facebook.com" },
};
