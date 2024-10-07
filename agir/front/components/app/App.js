import React from "react";
import { GlobalContextProvider } from "@agir/front/globalContext/GlobalContext";
import SWRContext from "@agir/front/allPages/SWRContext";

import PushModal from "@agir/front/allPages/PushModal/PushModal";

import Router from "./Router";

export default function App() {
  return (
    <SWRContext>
      <GlobalContextProvider hasRouter hasToasts>
        <Router>
          <PushModal isActive />
        </Router>
      </GlobalContextProvider>
    </SWRContext>
  );
}
