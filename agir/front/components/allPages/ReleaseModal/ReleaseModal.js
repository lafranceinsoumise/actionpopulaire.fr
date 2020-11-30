import React from "react";

import Modal from "@agir/front/genericComponents/Modal";
import Steps from "./Steps";

export const ReleaseModal = () => {
  const [shouldShow, setShouldShow] = React.useState(true);
  const handleClose = React.useCallback(() => {
    setShouldShow(false);
  }, []);

  return (
    <Modal shouldShow={shouldShow}>
      <Steps onClose={handleClose} />
    </Modal>
  );
};

export default ReleaseModal;
