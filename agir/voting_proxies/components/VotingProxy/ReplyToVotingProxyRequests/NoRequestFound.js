import PropTypes from "prop-types";
import React from "react";

import Spacer from "@agir/front/genericComponents/Spacer";

const NoRequestFound = ({ hasMatchedRequests }) => (
  <div>
    <h2
      css={`
        color: ${({ theme }) => theme.primary500};
      `}
    >
      Se porter volontaire pour prendre une procuration
    </h2>
    <Spacer size="2rem" />
    {hasMatchedRequests ? (
      <p>
        Cette demande de procuration a été déjà acceptée par quelqu'un d'autre
        ou a été annulée.
      </p>
    ) : (
      <p>Aucune demande de procuration n'a été trouvée près de chez vous.</p>
    )}
    <Spacer size="1rem" />
    <p>
      Nous vous recontacterons dès qu'une nouvelle personne aura demandé une
      procuration.
    </p>
  </div>
);
NoRequestFound.propTypes = {
  hasMatchedRequests: PropTypes.bool,
};
export default NoRequestFound;
