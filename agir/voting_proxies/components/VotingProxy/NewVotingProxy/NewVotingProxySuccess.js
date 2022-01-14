import React from "react";

import FormSuccess from "@agir/voting_proxies/Common/FormSuccess";
import Spacer from "@agir/front/genericComponents/Spacer";

const NewVotingProxySuccess = () => (
  <FormSuccess>
    <h2>Demande enregistrée</h2>
    <Spacer size="0.875rem" />
    <p>Vos disponibilités ont bien été enregistrées.</p>
    <p>
      Nous vous recontacterons dès qu'un·e demande de procuration sera créée
      près de chez vous.
    </p>
    <Spacer size="0.875rem" />
    <p>Merci de votre engagement&nbsp;!</p>
  </FormSuccess>
);

export default NewVotingProxySuccess;
