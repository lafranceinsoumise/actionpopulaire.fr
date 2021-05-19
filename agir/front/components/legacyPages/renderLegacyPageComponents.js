import React from "react";

import onDOMReady from "@agir/lib/utils/onDOMReady";
import { renderReactComponent } from "@agir/lib/utils/react";

import GlobalContextProvider from "@agir/front/globalContext/GlobalContext";
import PushModal from "@agir/front/allPages/PushModal";
import FeedbackButton from "@agir/front/allPages/FeedbackButton";
import TopBar from "@agir/front/allPages/TopBar";

const renderLegacyPageComponents = () => {
  const root = document.createElement("div");
  document.body.appendChild(root);
  renderReactComponent(
    <GlobalContextProvider>
      <TopBar hideBannerDownload />
      <PushModal isActive />
      <FeedbackButton />
    </GlobalContextProvider>,
    root
  );
};

onDOMReady(renderLegacyPageComponents);
