import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import { Interval, DateTime } from "luxon";

import Button from "@agir/front/genericComponents/Button";
import { useGlobalContext } from "@agir/front/genericComponents/GlobalContext";
import style from "@agir/front/genericComponents/_variables.scss";
import { Hide } from "@agir/front/genericComponents/grid";
import CSRFProtectedForm from "@agir/front/genericComponents/CSRFProtectedForm";
import { displayHumanDate } from "@agir/lib/utils/time";

const EventHeaderContainer = styled.div`
  @media (min-width: ${style.collapse}px) {
    margin-bottom: 4rem;
  }
  > * {
    margin: 0.5rem 0;
  }
`;

const EventTitle = styled.h1`
  font-size: 1.75rem;
  line-height: 1.4;
  font-weight: 700;
  margin-bottom: 0;

  @media (max-width: ${style.collapse}px) {
    margin-bottom: 1rem;
    font-size: 1.25rem;
  }
`;

const EventDate = styled.div`
  margin: 0.5rem 0;
  font-weight: 500;
`;

const SmallText = styled.div`
  font-size: 0.81rem;
  font-color: ${style.black500};
`;

/* Bouton qui prend 100 % de la largeur en petits écrans */
const ActionButton = styled(Button)`
  margin: 0.5rem 0;
  display: block;
  width: 100%;

  @media only screen and (min-width: 501px) {
    display: inline-block;
    width: auto;

    & + & {
      margin-left: 0.5rem;
    }
  }
`;

const ActionLink = styled.a`
  font-weight: 700;
  text-decoration: underline;
`;

const ActionButtons = (props) => {
  const {
    hasSubscriptionForm,
    past,
    rsvped,
    logged,
    isOrganizer,
    routes,
  } = props;

  if (past) {
    return <Button color="unavailable">Événement terminé</Button>;
  }

  if (!logged) {
    return (
      <ActionButton color="secondary" disabled={true}>
        Participer à l'événement
      </ActionButton>
    );
  }

  if (rsvped) {
    return (
      <>
        <ActionButton icon="check" color="confirmed">
          Je participe
        </ActionButton>
        {isOrganizer && (
          <ActionButton icon="settings" as="a" href={routes.manage}>
            Gérer l'événement
          </ActionButton>
        )}
      </>
    );
  }

  if (hasSubscriptionForm) {
    return (
      <ActionButton as="a" color="secondary" href={routes.join}>
        Participer à l'événement
      </ActionButton>
    );
  }

  return (
    <CSRFProtectedForm method="post" action={routes.join}>
      <ActionButton type="submit" color="secondary">
        Participer à l'événement
      </ActionButton>
    </CSRFProtectedForm>
  );
};
ActionButtons.propTypes = {
  hasSubscriptionForm: PropTypes.bool,
  past: PropTypes.bool,
  rsvped: PropTypes.bool,
  logged: PropTypes.bool,
  isOrganizer: PropTypes.bool,
  routes: PropTypes.object,
};

const AdditionalMessage = ({ logged, rsvped, price, routes }) => {
  if (!logged) {
    return (
      <div>
        <ActionLink href={routes.logIn}>Je me connecte</ActionLink> ou{" "}
        <ActionLink href={routes.signIn}>je m'inscris</ActionLink> pour
        participer à l'événement
      </div>
    );
  }

  if (rsvped) {
    return (
      <SmallText>
        <a href={routes.cancel}>Annuler ma participation</a>
      </SmallText>
    );
  }

  if (price) {
    return (
      <SmallText>
        <strong>Entrée&nbsp;: </strong>
        {price}
      </SmallText>
    );
  }

  return (
    <SmallText>Votre email sera communiquée à l'organisateur.rice</SmallText>
  );
};
AdditionalMessage.propTypes = {
  hasSubscriptionForm: PropTypes.bool,
  past: PropTypes.bool,
  rsvped: PropTypes.bool,
  logged: PropTypes.bool,
  isOrganizer: PropTypes.bool,
  price: PropTypes.string,
  routes: PropTypes.object,
};

const EventHeader = ({
  name,
  rsvp,
  options,
  schedule,
  routes,
  isOrganizer,
  hasSubscriptionForm,
}) => {
  const config = useGlobalContext();
  const logged = config.user !== null;
  const rsvped = !!rsvp;
  const now = DateTime.local();
  const past = now > schedule.start;
  let eventString = displayHumanDate(schedule.start);
  eventString = eventString.slice(0, 1).toUpperCase() + eventString.slice(1);

  return (
    <EventHeaderContainer>
      <EventTitle>{name}</EventTitle>
      <Hide under>
        <EventDate>{eventString}</EventDate>
      </Hide>
      <ActionButtons
        hasSubscriptionForm={hasSubscriptionForm}
        past={past}
        logged={logged}
        rsvped={rsvped}
        routes={routes}
        isOrganizer={isOrganizer}
      />
      {!past && (
        <AdditionalMessage
          past={past}
          logged={logged}
          rsvped={rsvped}
          price={options.price}
          routes={{ ...routes, ...config.routes }}
        />
      )}
    </EventHeaderContainer>
  );
};

EventHeader.propTypes = {
  name: PropTypes.string,
  schedule: PropTypes.instanceOf(Interval),
  hasSubscriptionForm: PropTypes.bool,
  isOrganizer: PropTypes.bool,
  options: PropTypes.shape({
    price: PropTypes.string,
  }),
  rsvp: PropTypes.string,
  routes: PropTypes.object,
};

export default EventHeader;
