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
  const [active, setActive] = useState(null);

  const { isMobileApp } = useMobileApp();

  const [ReferralModalAnnouncement, dismissReferralAnnouncement] =
    useCustomAnnouncement("ReferralModalAnnouncement");

  const [MobileAppAnnouncement, dismissMobileAppAnnouncement] =
    useCustomAnnouncement("MobileAppAnnouncement");

  const handleCloseReferral = useCallback(() => {
    setShouldShow(false);
    dismissReferralAnnouncement && dismissReferralAnnouncement();
  }, [dismissReferralAnnouncement]);

  const handleCloseMobileApp = useCallback(() => {
    setShouldShow(false);
    dismissMobileAppAnnouncement && dismissMobileAppAnnouncement();
  }, [dismissMobileAppAnnouncement]);

  useEffect(() => {
    if (
      isSessionLoaded &&
      isActive &&
      typeof shouldShow !== "boolean" &&
      !active &&
      !!ReferralModalAnnouncement
    ) {
      setActive("ReferralModalAnnouncement");
    }
  }, [
    shouldShow,
    isActive,
    isSessionLoaded,
    active,
    ReferralModalAnnouncement,
  ]);

  useEffect(() => {
    if (
      isSessionLoaded &&
      isActive &&
      typeof shouldShow !== "boolean" &&
      active !== "MobileAppAnnouncement" &&
      !!MobileAppAnnouncement &&
      !isMobileApp
    ) {
      setActive("MobileAppAnnouncement");
    }
  }, [
    shouldShow,
    isActive,
    isSessionLoaded,
    active,
    MobileAppAnnouncement,
    isMobileApp,
  ]);

  useEffect(() => {
    let displayTimeout;
    if (active) {
      displayTimeout = setTimeout(() => {
        window.location?.pathname &&
          !routeConfig.tellMore.match(window.location.pathname) &&
          setShouldShow(true);
      }, 1000);
    }
    return () => {
      clearTimeout(displayTimeout);
    };
  }, [active]);

  if (active === "MobileAppAnnouncement") {
    return (
      <MobileAppModal onClose={handleCloseMobileApp} shouldShow={shouldShow} />
    );
  }

  if (active === "ReferralModalAnnouncement") {
    return (
      <ReferralModal
        onClose={handleCloseReferral}
        shouldShow={shouldShow}
        referralURL={routes?.nspReferral}
      />
    );
  }

  return null;
};
PushModal.propTypes = {
  isActive: PropTypes.bool,
};

export default PushModal;
