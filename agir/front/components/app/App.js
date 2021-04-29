import { Helmet } from "react-helmet";
import React from "react";

import { GlobalContextProvider } from "@agir/front/globalContext/GlobalContext";

import PushModal from "@agir/front/allPages/PushModal/PushModal";

import Router from "./Router";

export default function App() {
  return (
    <GlobalContextProvider hasRouter hasToasts>
      <Router>
        <Helmet>
          <title>Action Populaire</title>
        </Helmet>
        <PushModal isActive />
      </Router>
    </GlobalContextProvider>
  );
}
