import PropTypes from "prop-types";
import React from "react";

import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";

import DesktopGroupPage, { DesktopGroupPageSkeleton } from "./DesktopGroupPage";
import MobileGroupPage, { MobileGroupPageSkeleton } from "./MobileGroupPage";

export const GroupPage = (props) => {
  const { isLoading } = props;
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
      <ResponsiveLayout
        {...props}
        groupSuggestions={[]}
        MobileLayout={MobileGroupPage}
        DesktopLayout={DesktopGroupPage}
      />
    </PageFadeIn>
  );
};
GroupPage.propTypes = {
  isLoading: PropTypes.bool,
};
export default GroupPage;
