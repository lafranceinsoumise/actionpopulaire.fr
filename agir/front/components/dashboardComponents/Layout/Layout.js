import React, { Suspense } from "react";

import { useResponsiveMemo } from "@agir/front/genericComponents/grid";

import { lazy } from "@agir/front/app/utils";

const MobileLayout = lazy(() => import("./MobileLayout"));
const DesktopLayout = lazy(() => import("./DesktopLayout"));

const Layout = (props) => {
  const Component = useResponsiveMemo(MobileLayout, DesktopLayout);
  return (
    <Suspense fallback={<div />}>
      <Component {...props} />
    </Suspense>
  );
};

export default Layout;
