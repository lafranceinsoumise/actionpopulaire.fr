import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";
import { useTimeout } from "react-use";

import UpdateAddressModal from "./UpdateAddressModal";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getIsSessionLoaded,
  getUser,
} from "@agir/front/globalContext/reducers";

import { routeConfig } from "@agir/front/app/routes.config";

export const PushModal = ({ isActive = true }) => {
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const user = useSelector(getUser);

  const [isReady, _, resetTimeout] = useTimeout(2000);
  const [shouldShow, setShouldShow] = useState(null);
  const [active, setActive] = useState(null);

  const currentPath = window?.location?.pathname;
  const isHomepage = !!currentPath && !!routeConfig.events.match(currentPath);
  const mayShow = !routeConfig.tellMore.match(currentPath) && isReady();

  const handleClose = useCallback(() => {
    setShouldShow(false);
  }, []);

  useEffect(() => {
    currentPath && resetTimeout();
  }, [currentPath, resetTimeout]);

  useEffect(() => {
    active && mayShow && setShouldShow(true);
  }, [active, mayShow]);

  useEffect(() => {
    if (!isSessionLoaded || !isActive || typeof shouldShow === "boolean") {
      return;
    }
    if (isHomepage && !!user && !user.zip) {
      active !== "UpdateAddressModal" && setActive("UpdateAddressModal");
      return;
    }
  }, [shouldShow, isActive, isSessionLoaded, active, user, isHomepage]);

  if (active === "UpdateAddressModal") {
    return (
      <UpdateAddressModal
        shouldShow={shouldShow}
        onClose={handleClose}
        user={user}
      />
    );
  }

  return null;
};
PushModal.propTypes = {
  isActive: PropTypes.bool,
};

export default PushModal;
