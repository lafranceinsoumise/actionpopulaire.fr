import React from "react";

import onDOMReady from "@agir/lib/utils/onDOMReady";
import { renderReactComponent } from "@agir/lib/utils/react";

import GlobalContextProvider from "@agir/front/globalContext/GlobalContext";
import PushModal from "@agir/front/allPages/PushModal";
import FeedbackButton from "@agir/front/allPages/FeedbackButton";
import { TopBar } from "@agir/front/allPages/TopBar/TopBar";
import SWRContext from "@agir/front/allPages/SWRContext";

const renderLegacyPageComponents = () => {
  const root = document.createElement("div");
  document.body.appendChild(root);
  const hideFeedbackButton =
    !!window?.Agir?.hideFeedbackButton ||
    document.querySelectorAll("[method='post']")?.length > 0;

  renderReactComponent(
    <SWRContext>
      <GlobalContextProvider>
        <>
          <TopBar hideBannerDownload />
          <PushModal isActive />
          {hideFeedbackButton ? null : <FeedbackButton />}
        </>
      </GlobalContextProvider>
    </SWRContext>,
    root
  );
};

onDOMReady(renderLegacyPageComponents);
