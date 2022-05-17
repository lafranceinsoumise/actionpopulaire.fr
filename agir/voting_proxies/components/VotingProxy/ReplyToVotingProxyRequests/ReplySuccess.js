import PropTypes from "prop-types";
import React from "react";

import FormSuccess from "@agir/elections/Common/FormSuccess";
import Spacer from "@agir/front/genericComponents/Spacer";

const ReplySuccess = ({ isAvailable }) => (
  <FormSuccess>
    <h2>Demande enregistrée</h2>
    <Spacer size="0.875rem" />
    {isAvailable ? (
      <p>
        Nous vous recontacterons dès que l'établissement de la procuration aura
        été confirmée.
      </p>
    ) : (
      <p>
        Votre indisponibilité pour prendre une procuration de vote a bien été
        enregistrée.
      </p>
    )}
    <Spacer size="0.875rem" />
    <p>Merci de votre engagement&nbsp;!</p>
  </FormSuccess>
);
ReplySuccess.propTypes = {
  isAvailable: PropTypes.bool.isRequired,
};
export default ReplySuccess;
