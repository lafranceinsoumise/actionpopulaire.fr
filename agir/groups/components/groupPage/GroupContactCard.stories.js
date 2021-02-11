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
    referentGender,
    contactName,
    contactPhone,
    contactEmail,
  } = args;
  const referents = [
    { displayName: "Isabelle Guérini", gender: "F" },
    {
      displayName: referentName,
      avatar: referentAvatar,
      gender: referentGender,
    },
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
  referentGender: "O",
  contactName: "Isabelle Guérini",
  contactEmail: "isabelini@gmail.com",
  contactPhone: "06 42 23 12 01",
};
