import { Helmet } from "react-helmet";
import React from "react";

import { GlobalContextProvider } from "@agir/front/globalContext/GlobalContext";
import Router from "./Router";
import PushModal from "@agir/front/allPages/PushModal";

export default function App() {
  return (
    <GlobalContextProvider>
      <Router>
        <Helmet>
          <title>Plateforme d'action - Action populaire</title>
        </Helmet>
        <PushModal isActive />
      </Router>
    </GlobalContextProvider>
  );
}
