import PropTypes from "prop-types";
import React from "react";

import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";
import Footer from "@agir/front/dashboardComponents/Footer";

// import DesktopGroupPage, { DesktopGroupPageSkeleton } from "./DesktopGroupPage";
// import MobileGroupPage, { MobileGroupPageSkeleton } from "./MobileGroupPage";

export const GroupSettings = (props) => {
  return (
    //   <ResponsiveLayout
    //     {...props}
    //     MobileLayout={MobileGroupSettings}
    //     DesktopLayout={DesktopGroupSettings}
    //   />
    <></>
  );
};
GroupSettings.propTypes = {
  isLoading: PropTypes.bool,
  activeTab: PropTypes.string,
};
export default GroupSettings;
