import PropTypes from "prop-types";
import React, { useEffect } from "react";

import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";
import Footer from "@agir/front/dashboardComponents/Footer";

import DesktopGroupPage, { DesktopGroupPageSkeleton } from "./DesktopGroupPage";
import MobileGroupPage, { MobileGroupPageSkeleton } from "./MobileGroupPage";
import NotFoundPage from "@agir/front/notFoundPage/NotFoundPage.js";

export const GroupPage = (props) => {
  const { isLoading, group } = props;

  return (
    <PageFadeIn
      ready={!isLoading}
      wait={
        <ResponsiveLayout
          DesktopLayout={DesktopGroupPageSkeleton}
          MobileLayout={MobileGroupPageSkeleton}
        />
      }
    >
      {group === false ? (
        <NotFoundPage isTopBar={false} title="Groupe" subtitle="Ce groupe" />
      ) : (
        <ResponsiveLayout
          {...props}
          MobileLayout={MobileGroupPage}
          DesktopLayout={DesktopGroupPage}
        />
      )}
      <Footer />
    </PageFadeIn>
  );
};
GroupPage.propTypes = {
  isLoading: PropTypes.bool,
  activeTab: PropTypes.string,
};
export default GroupPage;
