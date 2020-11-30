import Cookies from "js-cookie";
import PropTypes from "prop-types";
import React from "react";

import Modal from "@agir/front/genericComponents/Modal";
import Steps from "./Steps";

const COOKIE_CONFIG = {
  name: "AP_relmod",
  options: {
    expires: 730,
    secure: true,
  },
};

export const ReleaseModal = (withCookie = false) => {
  const [shouldShow, setShouldShow] = React.useState(false);
  const handleClose = React.useCallback(() => {
    setShouldShow(false);
  }, []);

  React.useEffect(() => {
    if (!withCookie) {
      setShouldShow(true);
      return;
    }
    const cookie = Cookies.get("AP_release");
    if (cookie) {
      return;
    }
    Cookies.set(COOKIE_CONFIG.name, "1", COOKIE_CONFIG.options);
    setShouldShow(true);
    // eslint-disable-next-line
  }, []);

  return (
    <Modal shouldShow={shouldShow}>
      <Steps onClose={handleClose} />
    </Modal>
  );
};
ReleaseModal.propTypes = {
  withCookie: PropTypes.bool,
};

export default ReleaseModal;
