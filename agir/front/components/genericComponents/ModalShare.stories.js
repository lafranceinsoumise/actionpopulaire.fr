import React from "react";
import ModalShare from "./ModalShare";

export default {
  component: ModalShare,
  title: "Generic/ModalShare",
};

const Template = ({ shouldShow, url }) => {
  const [isOpen, setIsOpen] = React.useState(shouldShow);
  React.useEffect(() => {
    setIsOpen(shouldShow);
  }, [shouldShow]);
  const handleClose = React.useCallback(() => {
    setIsOpen(false);
  }, []);
  return <ModalShare shouldShow={isOpen} onClose={handleClose} url={url} />;
};

export const Default = Template.bind({});
Default.args = {
  shouldShow: true,
  url: "https://actionpopulaire.fr",
};
