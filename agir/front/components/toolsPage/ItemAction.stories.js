import React from "react";

import { ItemAction } from "./ToolsPage";

export default {
  component: ItemAction,
  title: "Dashboard/PageTools/ItemAction",
};

const Template = (args) => {
  return (
    <div
      style={{
        width: "100vw",
        height: "100vh",
        padding: "20vh 20vw",
      }}
    >
      <ItemAction {...args} />
    </div>
  );
};

export const Default = Template.bind({});
Default.args = {
  title: "Une action vaut mieux que deux tu l'auras",
  href: "https://infos.actionpopulaire.fr/evenements/faire-connaitre-nos-sites-sur-twitter/",
  image:
    "https://infos.actionpopulaire.fr/wp-content/uploads/2021/03/Capture-de%CC%81cran-2021-03-03-a%CC%80-16.02.35-e1614783803610.png",
};

export const Static = Template.bind({});
Static.args = {
  ...Default.args,
  isStatic: true,
};
