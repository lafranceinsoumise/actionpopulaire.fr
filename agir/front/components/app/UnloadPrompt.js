import PropTypes from "prop-types";
import React from "react";
import { Prompt } from "react-router-dom";
import { useBeforeUnload } from "react-use";

const DEFAULT_MESSAGE =
  "Cette page vous demande de confirmer sa fermeture; des données que vous avez saisies pourraient ne pas être enregistrées. Confirmez-vous vouloir quitter la page ?";

const UnloadPrompt = (props) => {
  const { enabled, message = DEFAULT_MESSAGE } = props;
  useBeforeUnload(enabled, message);
  return <Prompt when={enabled} message={message} />;
};
UnloadPrompt.propTypes = {
  enabled: PropTypes.bool,
  message: PropTypes.string,
};

export default UnloadPrompt;
