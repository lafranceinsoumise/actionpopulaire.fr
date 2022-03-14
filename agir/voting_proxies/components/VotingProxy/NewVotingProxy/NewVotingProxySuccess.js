import PropTypes from "prop-types";
import React from "react";

import Button from "@agir/front/genericComponents/Button";
import FormSuccess from "@agir/voting_proxies/Common/FormSuccess";
import Spacer from "@agir/front/genericComponents/Spacer";

const NewVotingProxySuccess = ({ votingProxy }) => (
  <FormSuccess>
    <h2>Demande enregistrée</h2>
    <Spacer size="0.875rem" />
    <p>Vos disponibilités ont bien été enregistrées.</p>
    <Spacer size="0.875rem" />
    <p>
      Vous pouvez vérifier tout de suite si une demande est en attente, ou alors
      nous vous recontacterons dès qu'un·e demande de procuration sera créée
      près de chez vous.
    </p>
    <Spacer size="0.875rem" />
    <p>Merci de votre engagement&nbsp;!</p>
    <Spacer size="1rem" />
    <Button
      link
      color="primary"
      route="replyToVotingProxyRequests"
      routeParams={{
        votingProxyPk: votingProxy.id,
      }}
    >
      Voir si une demande est en attente près de chez moi
    </Button>
  </FormSuccess>
);

NewVotingProxySuccess.propTypes = {
  votingProxy: PropTypes.shape({
    id: PropTypes.string,
  }),
};

export default NewVotingProxySuccess;
