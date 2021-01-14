import React from "react";

import GroupContactCard from "./GroupContactCard";

export default {
  component: GroupContactCard,
  title: "Group/GroupContactCard",
};

const Template = (args) => {
  const {
    referentName,
    referentAvatar,
    contactName,
    contactPhone,
    contactEmail,
  } = args;
  const referents = [
    { fullName: "Isabelle Guérini" },
    { fullName: referentName, avatar: referentAvatar },
  ];
  const contact =
    contactName || contactEmail || contactPhone
      ? {
          name: contactName,
          email: contactEmail,
          phone: contactPhone,
        }
      : null;
  return <GroupContactCard referents={referents} contact={contact} />;
};

export const Default = Template.bind({});
Default.args = {
  referentName: "Serge Buchet",
  referentAvatar: "https://www.fillmurray.com/180/180",
  contactName: "Isabelle Guérini",
  contactEmail: "isabelini@gmail.com",
  contactPhone: "06 42 23 12 01",
};
