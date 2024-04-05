import PropTypes from "prop-types";
import React from "react";

import Button from "@agir/front/genericComponents/Button";
import FormSuccess from "@agir/elections/Common/FormSuccess";
import Spacer from "@agir/front/genericComponents/Spacer";

const NewVotingProxySuccess = ({ votingProxy }) => (
  <FormSuccess>
    <h2>
      Votre proposition d'être volontaire pour prendre une procuration a bien
      été enregistrée !
    </h2>
    <Spacer size="2rem" />
    <p>
      Vous pouvez vérifier tout de suite si une demande de procuration est en
      attente ou nous vous contacterons dès qu'une personne cherchera à donner
      une procuration près de chez vous.
    </p>
    <Spacer size="0.875rem" />
    <p>Merci pour votre disponibilité et votre aide !</p>
    <Spacer size="2rem" />
    <Button
      link
      wrap
      icon="arrow-right"
      color="primary"
      route="replyToVotingProxyRequests"
      routeParams={{
        votingProxyPk: votingProxy?.id,
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
