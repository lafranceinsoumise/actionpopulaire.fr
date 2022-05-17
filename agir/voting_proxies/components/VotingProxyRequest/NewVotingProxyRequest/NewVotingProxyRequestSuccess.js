import React from "react";

import FormSuccess from "@agir/elections/Common/FormSuccess";
import Spacer from "@agir/front/genericComponents/Spacer";

const NewVotingProxyRequestSuccess = () => (
  <FormSuccess>
    <h2>Demande envoyée</h2>
    <Spacer size="0.875rem" />
    <p>
      La demande de prise de votre procuration sera envoyée à des soutiens de
      Jean‑Luc Mélenchon de votre commune&nbsp;/&nbsp; circonscription
      consulaire.
    </p>
    <Spacer size="0.875rem" />
    <p>
      <strong>Vous recevrez un SMS et un e-mail</strong> lorsqu’une personne se
      manifestera pour porter votre procuration. Vous pourrez alors prendre
      contact avec elle et établir la procuration avec ses informations
      personnelles.
    </p>
  </FormSuccess>
);

export default NewVotingProxyRequestSuccess;
