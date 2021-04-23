import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";

import ReferralModal from "./ReferralModal";
import MobileAppModal from "./MobileAppModal";

import { useMobileApp } from "@agir/front/app/hooks";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getIsSessionLoaded,
  getRoutes,
} from "@agir/front/globalContext/reducers";

import { useCustomAnnouncement } from "@agir/activity/common/hooks";
import { routeConfig } from "@agir/front/app/routes.config";

export const PushModal = ({ isActive = true }) => {
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const routes = useSelector(getRoutes);

  const [shouldShow, setShouldShow] = useState(null);

  const { isMobileApp } = useMobileApp();

  const [
    ReferralModalAnnouncement,
    dismissReferralAnnouncement,
  ] = useCustomAnnouncement("ReferralModalAnnouncement");

  const [
    MobileAppAnnouncement,
    dismissMobileAppAnnouncement,
  ] = useCustomAnnouncement("MobileAppAnnouncement");

  const handleCloseReferral = useCallback(() => {
    setShouldShow(false);
    dismissReferralAnnouncement && dismissReferralAnnouncement();
  }, [dismissReferralAnnouncement]);

  const handleCloseMobileApp = useCallback(() => {
    setShouldShow(false);
    dismissMobileAppAnnouncement && dismissMobileAppAnnouncement();
  }, [dismissMobileAppAnnouncement]);

  useEffect(() => {
    let displayTimeout;
    if (
      isActive &&
      isSessionLoaded &&
      typeof shouldShow !== "boolean" &&
      (!!ReferralModalAnnouncement || !!MobileAppAnnouncement)
    ) {
      displayTimeout = setTimeout(() => {
        window.location?.pathname &&
          !routeConfig.tellMore.match(window.location.pathname) &&
          setShouldShow(true);
      }, 1000);
    }
    return () => {
      clearTimeout(displayTimeout);
    };
  }, [
    shouldShow,
    isActive,
    isSessionLoaded,
    ReferralModalAnnouncement,
    MobileAppAnnouncement,
  ]);

  if (MobileAppAnnouncement && !isMobileApp) {
    return (
      <MobileAppModal onClose={handleCloseMobileApp} shouldShow={shouldShow} />
    );
  }

  return (
    <ReferralModal
      onClose={handleCloseReferral}
      shouldShow={shouldShow}
      referralURL={
        isSessionLoaded && routes.nspReferral ? routes.nspReferral : ""
      }
    />
  );
};
PushModal.propTypes = {
  isActive: PropTypes.bool,
};

export default PushModal;
