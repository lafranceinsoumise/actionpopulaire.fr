import { Helmet } from "react-helmet";
import React from "react";

import { GlobalContextProvider } from "@agir/front/globalContext/GlobalContext";
import Router from "./Router";
import TopBar from "@agir/front/allPages/TopBar";
import PushModal from "@agir/front/allPages/PushModal";

export default function App() {
  return (
    <GlobalContextProvider>
      <Router>
        <Helmet>
          <title>Plateforme d'action - Action populaire</title>
        </Helmet>
        <TopBar />
        <PushModal isActive />
      </Router>
    </GlobalContextProvider>
  );
}
