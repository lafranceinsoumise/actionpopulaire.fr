import React, { Suspense } from "react";

import { useResponsiveMemo } from "@agir/front/genericComponents/grid";

import { lazy } from "@agir/front/app/utils";

import MobileLayout from "./MobileLayout";
import DesktopLayout from "./DesktopLayout";

const Layout = (props) => {
  const Component = useResponsiveMemo(MobileLayout, DesktopLayout);
  return <Component {...props} />;
};

export default Layout;
