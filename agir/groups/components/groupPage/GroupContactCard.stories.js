import React from "react";

import GroupContactCard from "./GroupContactCard";

export default {
  component: GroupContactCard,
  title: "Group/GroupContactCard",
};

const Template = (args) => {
  const {
    managerName,
    managerAvatar,
    managerGender,
    contactName,
    contactPhone,
    contactEmail,
  } = args;
  const managers = [
    { displayName: "Isabelle Guérini", gender: "F" },
    { displayName: managerName, avatar: managerAvatar, gender: managerGender },
  ];
  const contact =
    contactName || contactEmail || contactPhone
      ? {
          name: contactName,
          email: contactEmail,
          phone: contactPhone,
        }
      : null;
  return <GroupContactCard managers={managers} contact={contact} />;
};

export const Default = Template.bind({});
Default.args = {
  managerName: "Serge Buchet",
  managerAvatar: "https://www.fillmurray.com/180/180",
  managerGender: "O",
  contactName: "Isabelle Guérini",
  contactEmail: "isabelini@gmail.com",
  contactPhone: "06 42 23 12 01",
};
