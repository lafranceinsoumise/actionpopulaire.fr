import React from "react";

import UnavailableMessagePage from "./UnavailableMessagePage";
import { TestGlobalContextProvider } from "@agir/front/globalContext/GlobalContext";

export default {
  component: UnavailableMessagePage,
  title: "Group/UnavailableMessagePage",
};

const Template = (args) => {
  return (
    <TestGlobalContextProvider
      value={{ backLink: { href: "back", label: "Retour à l'accueil" } }}
    >
      <UnavailableMessagePage {...args} />
    </TestGlobalContextProvider>
  );
};

export const Default = Template.bind({});
Default.args = {
  groupURL: "#group",
};
