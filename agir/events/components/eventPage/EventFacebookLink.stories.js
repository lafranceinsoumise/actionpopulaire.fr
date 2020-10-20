import React from "react";

import EventFacebookLink from "./EventFacebookLink";

export default {
  component: EventFacebookLink,
  title: "Events/FacebookLink",
};

const Template = (args) => <EventFacebookLink {...args} />;

export const Default = Template.bind({});
Default.args = {
  routes: { facebook: "https://facebook.com" },
};
