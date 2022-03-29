import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";

import UpdateAddressModal from "./UpdateAddressModal";
import MobileAppModal from "./MobileAppModal";

import { useMobileApp } from "@agir/front/app/hooks";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getIsSessionLoaded,
  getUser,
} from "@agir/front/globalContext/reducers";

import { useCustomAnnouncement } from "@agir/activity/common/hooks";
import { routeConfig } from "@agir/front/app/routes.config";

export const PushModal = ({ isActive = true }) => {
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const user = useSelector(getUser);

  const [shouldShow, setShouldShow] = useState(null);
  const [active, setActive] = useState(null);
  const { isMobileApp } = useMobileApp();
  const isHomepage = routeConfig.events.match(window?.location?.pathname);

  const [MobileAppAnnouncement, dismissMobileAppAnnouncement] =
    useCustomAnnouncement("MobileAppAnnouncement");

  const handleClose = useCallback(() => {
    setShouldShow(false);
  }, []);

  const handleCloseMobileApp = useCallback(() => {
    setShouldShow(false);
    dismissMobileAppAnnouncement && dismissMobileAppAnnouncement();
  }, [dismissMobileAppAnnouncement]);

  useEffect(() => {
    if (!isSessionLoaded || !isActive || typeof shouldShow === "boolean") {
      return;
    }
    if (isHomepage && !!user && !user.zip) {
      active !== "UpdateAddressModal" && setActive("UpdateAddressModal");
      return;
    }
    if (!!MobileAppAnnouncement && !isMobileApp) {
      active !== "MobileAppAnnouncement" && setActive("MobileAppAnnouncement");
    }
  }, [
    shouldShow,
    isActive,
    isSessionLoaded,
    active,
    MobileAppAnnouncement,
    isMobileApp,
    user,
    isHomepage,
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

  if (active === "UpdateAddressModal") {
    return (
      <UpdateAddressModal
        shouldShow={shouldShow}
        onClose={handleClose}
        user={user}
      />
    );
  }

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
