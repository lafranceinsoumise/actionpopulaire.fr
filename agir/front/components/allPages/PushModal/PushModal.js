import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";
import ReferralModal from "./ReferralModal";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getIsSessionLoaded,
  getRoutes,
} from "@agir/front/globalContext/reducers";

import { useCustomAnnouncement } from "@agir/activity/common/hooks";

export const PushModal = ({ isActive = true }) => {
  const isSessionLoaded = useSelector(getIsSessionLoaded);
  const routes = useSelector(getRoutes);
  const [shouldShow, setShouldShow] = useState(false);
  const [ReferralModalAnnouncement, onClose] = useCustomAnnouncement(
    isActive && isSessionLoaded ? "ReferralModalAnnouncement" : null
  );
  const handleClose = useCallback(() => {
    setShouldShow(false);
    onClose && onClose();
  }, [onClose]);

  useEffect(() => {
    !!ReferralModalAnnouncement && setShouldShow(true);
  }, [ReferralModalAnnouncement]);

  return (
    <ReferralModal
      onClose={handleClose}
      shouldShow={shouldShow}
      referralURL={isSessionLoaded ? routes.nspReferral : ""}
    />
  );
};
PushModal.propTypes = {
  isActive: PropTypes.bool,
};

export default PushModal;
