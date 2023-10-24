import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import { useTimeout } from "react-use";

import UpdateAddressModal from "./UpdateAddressModal";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getIsSessionLoaded } from "@agir/front/globalContext/reducers";

import { routeConfig } from "@agir/front/app/routes.config";

export const PushModal = ({ isActive = true }) => {
  const isSessionLoaded = useSelector(getIsSessionLoaded);

  const [isReady, _, resetTimeout] = useTimeout(2000);
  const [active, setActive] = useState(null);

  const currentPath = window?.location?.pathname;
  const isHomepage = !!currentPath && !!routeConfig.events.match(currentPath);
  const mayShow =
    isActive &&
    isSessionLoaded &&
    isHomepage &&
    !routeConfig.tellMore.match(currentPath) &&
    isReady();

  useEffect(() => {
    currentPath && resetTimeout();
  }, [currentPath, resetTimeout]);

  useEffect(() => {
    if (mayShow) {
      active !== "UpdateAddressModal" && setActive("UpdateAddressModal");
    }
  }, [mayShow, active]);

  if (active === "UpdateAddressModal") {
    return <UpdateAddressModal />;
  }

  return null;
};
PushModal.propTypes = {
  isActive: PropTypes.bool,
};

export default PushModal;
