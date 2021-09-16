import PropTypes from "prop-types";
import React from "react";

import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";

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
        <NotFoundPage
          isTopBar={false}
          title="Groupe"
          subtitle="Ce groupe"
          reloadOnReconnection={false}
        />
      ) : (
        <ResponsiveLayout
          {...props}
          MobileLayout={MobileGroupPage}
          DesktopLayout={DesktopGroupPage}
        />
      )}
    </PageFadeIn>
  );
};
GroupPage.propTypes = {
  group: PropTypes.object,
  isLoading: PropTypes.bool,
  activeTab: PropTypes.string,
};
export default GroupPage;
