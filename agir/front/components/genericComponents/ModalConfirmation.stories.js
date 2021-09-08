import React, { useState, useCallback, useEffect } from "react";
import ModalConfirmation from "./ModalConfirmation";

export default {
  component: ModalConfirmation,
  title: "Generic/ModalConfirmation",
};

const Template = ({
  shouldShow,
  title,
  description,
  dismissLabel,
  confirmationLabel,
  confirmationUrl,
}) => {
  const [isOpen, setIsOpen] = useState(shouldShow);

  useEffect(() => {
    setIsOpen(shouldShow);
  }, [shouldShow]);

  const handleClose = useCallback(() => {
    setIsOpen(false);
  }, []);

  return (
    <ModalConfirmation
      shouldShow={isOpen}
      onClose={handleClose}
      title={title}
      description={description}
      dismissLabel={dismissLabel}
      confirmationLabel={confirmationLabel}
      confirmationUrl={confirmationUrl}
    />
  );
};

export const Default = Template.bind({});
Default.args = {
  shouldShow: true,
  title: "Titre de la modale",
  description: "Ma description est sacrée !",
};

export const WithConfirmation = Template.bind({});
WithConfirmation.args = {
  shouldShow: true,
  title: "Titre de la modale",
  description: "Ma description est sacrée :)",
  dismissLabel: "Non merci",
  confirmationLabel: "Allons à cette étape !",
  confirmationUrl: "https://actionpopulaire.fr",
};
