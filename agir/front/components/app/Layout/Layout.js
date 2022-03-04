import React from "react";

import { useResponsiveMemo } from "@agir/front/genericComponents/grid";

import MobileLayout from "./MobileLayout";
import DesktopLayout from "./DesktopLayout";

const Layout = (props) => {
  const Component = useResponsiveMemo(MobileLayout, DesktopLayout);
  return <Component {...props} />;
};

export default Layout;
