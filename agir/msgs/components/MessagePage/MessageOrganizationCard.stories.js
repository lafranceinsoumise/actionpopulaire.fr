import React from "react";

import MessageOrganizationCard from "./MessageOrganizationCard";

export default {
  component: MessageOrganizationCard,
  title: "Messages/MessagePage/MessageOrganizationCard",
};

const Template = (args) => {
  return (
    <div
      style={{
        width: "100%",
        height: "100vh",
        padding: "1.5rem",
      }}
    >
      <MessageOrganizationCard {...args} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  isLoading: false,
  user: {
    displayName: "MonSurnom",
    email: "mon@email.com",
  },
  group: {
    name: "Le groupe de Roquefort",
    referents: [
      {
        displayName: "Stéphanie",
      },
      {
        displayName: "Jacques",
      },
    ],
  },
};
