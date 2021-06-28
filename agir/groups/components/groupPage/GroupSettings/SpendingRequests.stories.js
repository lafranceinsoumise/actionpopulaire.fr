import React from "react";

import SpendingRequests from "./SpendingRequests.js";

export default {
  component: SpendingRequests,
  title: "GroupSettings/SpendingRequests",
};

const Template = (args) => <SpendingRequests {...args} />;

export const Default = Template.bind({});
Default.args = {
  newSpendingRequestLink: "#newSpendingRequest",
  spendingRequests: [
    {
      id: "3ae28ff9-6be9-43c7-b02a-76f99fa50821",
      title: "Achat d’un nouveau kakemono",
      status: "En attente de validation par un autre animateur",
      date: "2021-06-21T08:18:26.960861Z",
      link: "http://agir.local:8000/financement/requete/3ae28ff9-6be9-43c7-b02a-76f99fa50821/",
    },
    {
      id: "3ae28ff9-6be9-43c7-b02a-76f99fa50822",
      title: "Flyers présidentielles octobre 2021",
      status:
        "En attente de vérification par l'équipe de suivi des questions financières",
      date: "2021-06-21T08:18:26.960861Z",
      link: "http://agir.local:8000/financement/requete/3ae28ff9-6be9-43c7-b02a-76f99fa50822/",
    },
    {
      id: "3ae28ff9-6be9-43c7-b02a-76f99fa50823",
      title: "Achat d’un nouveau kakemono",
      status: "Brouillon à compléter",
      date: "2021-06-21T08:18:26.960861Z",
      link: "http://agir.local:8000/financement/requete/3ae28ff9-6be9-43c7-b02a-76f99fa50823/",
    },
  ],
};

export const Empty = Template.bind({});
Empty.args = {
  ...Default.args,
  spendingRequests: [],
};
