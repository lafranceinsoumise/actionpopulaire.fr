import React from "react";

import NewGroupPageModal from "./NewGroupPageModal";
import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";

export default {
  component: NewGroupPageModal,
  title: "Group/NewGroupPageModal",
};

const Template = (args) => {
  return (
    <TestGlobalContextProvider
      value={{ routes: { feedbackForm: "#feedbackForm" } }}
    >
      <NewGroupPageModal {...args} />
    </TestGlobalContextProvider>
  );
};

export const Default = Template.bind({});
Default.args = {
  isActive: true,
};
