import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";
import ReferralModal from "./ReferralModal";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getIsSessionLoaded,
  getRoutes,
  getUser,
} from "@agir/front/globalContext/reducers";

export const PushModal = ({ isActive = true }) => {
  const user = useSelector(getUser);
  const routes = useSelector(getRoutes);
  const isSessionLoaded = useSelector(getIsSessionLoaded);

  const [shouldShow, setShouldShow] = useState(false);
  const [activeModal, setActiveModal] = useState(null);

  const handleClose = useCallback(() => {
    setShouldShow(false);
  }, []);

  useEffect(() => {
    if (!isActive || typeof window === "undefined" || !window.localStorage) {
      setActiveModal(null);
      setShouldShow(false);
      return;
    }
    if (isSessionLoaded && !!user && user.is2022) {
      const shouldHide = window.localStorage.getItem("AP_refmod");
      if (!shouldHide) {
        window.localStorage.setItem("AP_refmod", "1");
        setActiveModal("referral");
        setShouldShow(true);
        return;
      }
    }
  }, [isSessionLoaded, user, isActive]);

  switch (activeModal) {
    case "referral":
      return (
        <ReferralModal
          onClose={handleClose}
          shouldShow={shouldShow}
          referralURL={routes.nspReferral}
        />
      );
    default:
      return null;
  }
};
PushModal.propTypes = {
  isActive: PropTypes.bool,
};

export default PushModal;
