import PropTypes from "prop-types";
import React from "react";

import Modal from "@agir/front/genericComponents/Modal";
import Steps from "./Steps";

import { useGlobalContext } from "@agir/front/genericComponents/GlobalContext";

export const ReleaseModal = ({ once = false, isActive = true }) => {
  const [shouldShow, setShouldShow] = React.useState(false);
  const handleClose = React.useCallback(() => {
    setShouldShow(false);
  }, []);

  React.useEffect(() => {
    if (!isActive) {
      setShouldShow(false);
      return;
    }
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
  }, [isActive, once]);

  return (
    <Modal shouldShow={shouldShow}>
      <Steps onClose={handleClose} />
    </Modal>
  );
};
ReleaseModal.propTypes = {
  once: PropTypes.bool,
  isActive: PropTypes.bool,
};

const ConnectedReleaseModal = (props) => {
  const { user } = useGlobalContext();
  return <ReleaseModal {...props} isActive={!!user} />;
};

export default ConnectedReleaseModal;
