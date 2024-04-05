import PropTypes from "prop-types";
import React from "react";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

const NoRequestFound = ({ hasMatchedRequests }) => (
  <div style={{ textAlign: "center" }}>
    <h2 style={{ textAlign: "left" }}>
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
    <Spacer size="3rem" />
    <footer>
      <Button color="dismiss" icon="arrow-right" link route="eu2024">
        Retourner sur le site
      </Button>
    </footer>
  </div>
);
NoRequestFound.propTypes = {
  hasMatchedRequests: PropTypes.bool,
};

export default NoRequestFound;
