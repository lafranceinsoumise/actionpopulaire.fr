import PropTypes from "prop-types";
import React from "react";

import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";

const NoRequestFound = ({
  hasMatchedRequests,
  hasMatchingLink,
  votingProxyPk,
}) => (
  <div style={{ textAlign: "center" }}>
    <h2>Se porter volontaire pour prendre une procuration</h2>
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
    {hasMatchingLink && votingProxyPk ? (
      <p>
        Vous pouvez vérifier tout de suite si une autre demande de procuration
        est en attente près de chez vous ou nous vous contacterons dès qu'une
        personne cherchera à donner une procuration.
      </p>
    ) : (
      <p>
        Nous vous recontacterons dès qu'une nouvelle personne aura demandé une
        procuration près de chez vous.
      </p>
    )}
    <Spacer size="2rem" />
    {hasMatchingLink && votingProxyPk && (
      <Button
        link
        wrap
        icon="arrow-right"
        color="primary"
        route="replyToVotingProxyRequests"
        routeParams={{ votingProxyPk }}
      >
        Voir si une autre demande est en attente près de chez moi
      </Button>
    )}
    <Spacer size="1rem" />
    <footer>
      <Button color="dismiss" icon="arrow-right" link route="legislative2024">
        Retourner sur le site
      </Button>
    </footer>
  </div>
);
NoRequestFound.propTypes = {
  hasMatchedRequests: PropTypes.bool,
  hasMatchingLink: PropTypes.bool,
  votingProxyPk: PropTypes.string,
};

export default NoRequestFound;
