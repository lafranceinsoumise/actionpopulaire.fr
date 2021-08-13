import PropTypes from "prop-types";
import React from "react";
import useSWR from "swr";

import * as api from "@agir/events/common/api";

import Link from "@agir/front/app/Link";
import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer.js";

import { StyledTitle } from "@agir/front/genericComponents/ObjectManagement/styledComponents.js";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel.js";

const EventCancelation = (props) => {
  const { onBack, illustration, eventPk } = props;

  const { data: event } = useSWR(api.getEventEndpoint("getEvent", { eventPk }));
  const cancelUrl = api.getEventEndpoint("cancelEvent", { eventPk });

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle>Annuler l'événement</StyledTitle>

      <Spacer size="1rem" />

      <p>
        Voulez-vous annuler votre événement <strong>{event.name}</strong> ?
      </p>
      <p>
        Tous les participant·es recevront une notification leur indiquant que
        vous avez annulé l’événement.
      </p>
      <p>Cette action est irréversible.</p>

      <Spacer size="1rem" />
      <Link route={cancelUrl}>
        <Button color="danger">Annuler l'événement</Button>
      </Link>
    </>
  );
};
EventCancelation.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  eventPk: PropTypes.string,
};
export default EventCancelation;
