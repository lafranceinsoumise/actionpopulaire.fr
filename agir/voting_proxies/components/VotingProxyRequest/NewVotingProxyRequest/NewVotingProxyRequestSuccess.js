import React from "react";

import FormSuccess from "@agir/elections/Common/FormSuccess";
import Spacer from "@agir/front/genericComponents/Spacer";

const NewVotingProxyRequestSuccess = () => (
  <FormSuccess>
    <h2>Votre demande a bien été enregistrée !</h2>
    <Spacer size="2rem" />
    <p>
      Votre demande de procuration sera envoyée aux insoumis·es de votre commune
      ou de votre circonscription consulaire.
    </p>
    <Spacer size="0.875rem" />
    <p>
      <strong>
        Vous recevrez un SMS et un e-mail lorsqu'une personne sera volontaire
        pour prendre votre procuration.
      </strong>{" "}
      Vous pourrez alors prendre contact avec elle et établir la procuration
      avec ses informations personnelles.
    </p>
    <Spacer size="1rem" />
  </FormSuccess>
);

export default NewVotingProxyRequestSuccess;
