import React from "react";

import { ResponsiveLayout } from "@agir/front/genericComponents/grid";

import DesktopLayout from "./DesktopLayout";
import MobileLayout from "./MobileLayout";

const SpendingRequestDetails = (props) => (
  <ResponsiveLayout
    {...props}
    MobileLayout={MobileLayout}
    DesktopLayout={DesktopLayout}
  />
);

export default SpendingRequestDetails;
