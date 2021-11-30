import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";
import useSWR from "swr";

import { ResponsiveLayout } from "@agir/front/genericComponents/grid";

import MobileActionToolsPage from "./MobileActionToolsPage";
import DesktopActionToolsPage from "./DesktopActionToolsPage";

const ActionToolsPage = (props) => {
  const { data: session } = useSWR("/api/session/");
  const { data: donations } = useSWR("/api/2022/dons/aggregats/");

  return (
    <ResponsiveLayout
      MobileLayout={MobileActionToolsPage}
      DesktopLayout={DesktopActionToolsPage}
      firstName={session?.user?.firstName}
      hasGroups={session?.user?.groups?.length > 0}
      city={session?.user?.city}
      commune={session?.user?.commune}
      donationAmount={donations?.totalAmount}
    />
  );
};

export default ActionToolsPage;
