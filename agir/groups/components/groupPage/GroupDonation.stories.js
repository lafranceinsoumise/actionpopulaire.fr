import React from "react";

import GroupDonation from "./GroupDonation";

export default {
  component: GroupDonation,
  title: "Group/GroupDonation",
};

const Template = (args) => {
  return (
    <div style={{ maxWidth: 396 }}>
      <GroupDonation {...args} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  url: "#dons",
  id: "12345",
  isCertified: true,
};
