import PropTypes from "prop-types";
import React from "react";

import Modal from "@agir/front/genericComponents/Modal";
import Steps from "./Steps";

export const ReleaseModal = ({ shouldShow = false, onClose }) => {
  return (
    <Modal shouldShow={shouldShow}>
      <Steps onClose={onClose} />
    </Modal>
  );
};
ReleaseModal.propTypes = {
  shouldShow: PropTypes.bool,
  onClose: PropTypes.func,
};

export default ReleaseModal;
