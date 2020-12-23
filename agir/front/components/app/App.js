import React from "react";

import { GlobalContextProvider } from "@agir/front/globalContext/GlobalContext";
import Router from "./Router";
import TopBar from "@agir/front/allPages/TopBar";
import PushModal from "@agir/front/allPages/PushModal";
import FeedbackButton from "@agir/front/allPages/FeedbackButton";

export default function App() {
  return (
    <GlobalContextProvider>
      <Router>
        <TopBar />
        <PushModal isActive />
        <FeedbackButton />
      </Router>
    </GlobalContextProvider>
  );
}
