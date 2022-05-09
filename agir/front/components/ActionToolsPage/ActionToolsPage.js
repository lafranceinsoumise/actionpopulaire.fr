import React from "react";
import useSWR from "swr";

import { ResponsiveLayout } from "@agir/front/genericComponents/grid";

import MobileActionToolsPage from "./MobileActionToolsPage";
import DesktopActionToolsPage from "./DesktopActionToolsPage";

const ActionToolsPage = () => {
  const { data: session } = useSWR("/api/session/");

  return (
    <ResponsiveLayout
      MobileLayout={MobileActionToolsPage}
      DesktopLayout={DesktopActionToolsPage}
      firstName={session?.user?.firstName}
      hasGroups={session?.user?.groups?.length > 0}
      city={session?.user?.city}
      commune={session?.user?.commune}
    />
  );
};

export default ActionToolsPage;
