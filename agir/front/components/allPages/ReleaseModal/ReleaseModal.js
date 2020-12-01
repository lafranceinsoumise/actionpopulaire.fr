import PropTypes from "prop-types";
import React from "react";

import Modal from "@agir/front/genericComponents/Modal";
import Steps from "./Steps";

const ReleaseModal = ({ once = false }) => {
  const [shouldShow, setShouldShow] = React.useState(false);
  const handleClose = React.useCallback(() => {
    setShouldShow(false);
  }, []);

  React.useEffect(() => {
    if (!once) {
      setShouldShow(true);
      return;
    }
    if (!window.localStorage) {
      return;
    }
    const shouldShow = window.localStorage.getItem("AP_relmod");
    if (shouldShow) {
      return;
    }
    window.localStorage.setItem("AP_relmod", "1");
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
  once: PropTypes.bool,
};

export default ReleaseModal;
