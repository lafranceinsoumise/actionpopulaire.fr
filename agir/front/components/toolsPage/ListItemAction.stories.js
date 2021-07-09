import React from "react";

import { ListItemAction } from "./ToolsPage";

export default {
  component: ListItemAction,
  title: "Dashboard/PageTools/ListItemAction",
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
      <ListItemAction {...args} />
    </div>
  );
};

const mockPage = {
  id: 15,
  category_id: 15,
  category_name: "Lire des bouquins",
  title: "Lire l'ère du peuple",
  link: "https://infos.actionpopulaire.fr/evenements/faire-connaitre-nos-sites-sur-twitter/",
  img: "https://infos.actionpopulaire.fr/wp-content/uploads/2021/03/Capture-de%CC%81cran-2021-03-03-a%CC%80-16.02.35-e1614783803610.png",
};
const mockPages = [
  mockPage,
  mockPage,
  mockPage,
  mockPage,
  mockPage,
  mockPage,
  mockPage,
];

export const Default = Template.bind({});
Default.args = {
  pages: mockPages,
};

export const Static = Template.bind({});
Static.args = {
  ...Default.args,
  isStatic: true,
};
