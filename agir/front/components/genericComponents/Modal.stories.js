import React from "react";
import Modal from "./Modal";

export default {
  component: Modal,
  title: "Generic/Modal",
};

const ModalContent = () => (
  <div
    style={{
      background: "white",
      height: "50%",
      width: "50%",
      margin: "5% auto",
      display: "flex",
      alignItems: "center",
      justifyContent: "center",
    }}
  >
    I am the modal content!
  </div>
);

const Template = ({ shouldShow }) => {
  const [isOpen, setIsOpen] = React.useState(shouldShow);
  React.useEffect(() => {
    setIsOpen(shouldShow);
  }, [shouldShow]);
  const handleClose = React.useCallback(() => {
    setIsOpen(false);
  }, []);
  return (
    <Modal shouldShow={isOpen} onClose={handleClose}>
      <ModalContent />
    </Modal>
  );
};

export const Default = Template.bind({});
Default.args = {
  shouldShow: true,
};
