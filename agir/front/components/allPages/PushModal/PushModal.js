import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";

import MobileAppModal from "./MobileAppModal";

import { useMobileApp } from "@agir/front/app/hooks";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getIsSessionLoaded } from "@agir/front/globalContext/reducers";

import { useCustomAnnouncement } from "@agir/activity/common/hooks";
import { routeConfig } from "@agir/front/app/routes.config";

export const PushModal = ({ isActive = true }) => {
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const [shouldShow, setShouldShow] = useState(null);
  const [active, setActive] = useState(null);

  const { isMobileApp } = useMobileApp();

  const [MobileAppAnnouncement, dismissMobileAppAnnouncement] =
    useCustomAnnouncement("MobileAppAnnouncement");

  const handleCloseMobileApp = useCallback(() => {
    setShouldShow(false);
    dismissMobileAppAnnouncement && dismissMobileAppAnnouncement();
  }, [dismissMobileAppAnnouncement]);

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

  return null;
};
PushModal.propTypes = {
  isActive: PropTypes.bool,
};

export default PushModal;
