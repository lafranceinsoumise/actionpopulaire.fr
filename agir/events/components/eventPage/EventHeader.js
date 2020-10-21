import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import { DateTime } from "luxon";

import Button from "@agir/front/genericComponents/Button";
import { useGlobalContext } from "@agir/front/genericComponents/GobalContext";
import style from "@agir/front/genericComponents/style.scss";
import { Hide } from "@agir/front/genericComponents/grid";
import CSRFProtectedForm from "@agir/front/genericComponents/CSRFProtectedForm";

const dateFormat = {
  weekday: "long",
  month: "long",
  day: "numeric",
  hour: "numeric",
  minute: "2-digit",
};

const EventHeaderContainer = styled.div`
  > * {
    margin: 0.5rem 0;
  }
`;

const EventTitle = styled.h1`
  font-size: 1.75rem;
  line-height: 1.4;
  font-weight: 800;
  margin-bottom: 0.5rem;
`;

const EventDate = styled.div`
  margin: 0.5rem 0;
`;

const SmallText = styled.div`
  font-size: 0.81rem;
  font-color: ${style.black500};
`;

/* Bouton qui prend 100 % de la largeur en petits écrans */
const ActionButton = styled(Button)`
  margin: 0.5rem 0;
  display: block;

  @media only screen and (min-width: 501px) {
    display: inline-block;
    & + & {
      margin-left: 0.5rem;
    }
  }
`;

const ActionButtons = ({
  hasSubscriptionForm,
  past,
  rsvped,
  logged,
  isOrganizer,
  routes,
}) => {
  if (past) {
    return <Button color="unavailable">Événement terminé</Button>;
  }

  if (logged) {
    if (rsvped) {
      return (
        <>
          <ActionButton icon="check-circle" color="confirmed">
            Je participe
          </ActionButton>
          {isOrganizer && (
            <ActionButton as="a" href={routes.manage}>
              Modifier l'événement
            </ActionButton>
          )}
        </>
      );
    } else {
      if (hasSubscriptionForm) {
        return (
          <ActionButton as="a" color="secondary" href={routes.attend}>
            Participer à l'événement
          </ActionButton>
        );
      } else {
        return (
          <CSRFProtectedForm method="post" action={routes.attend}>
            <ActionButton type="submit" color="secondary">
              Participer à l'événement
            </ActionButton>
          </CSRFProtectedForm>
        );
      }
    }
  } else {
    return (
      <ActionButton color="secondary" disabled={true}>
        Participer à l'événement
      </ActionButton>
    );
  }
};

const AdditionalMessage = ({ logged, rsvped, price, routes }) => {
  if (logged) {
    if (rsvped) {
      return (
        <SmallText>
          <a href={routes.cancel}>Annuler ma participation</a>
        </SmallText>
      );
    } else if (price) {
      return (
        <SmallText>
          <strong>Entrée :</strong>
          {price}
        </SmallText>
      );
    } else {
      return (
        <SmallText>
          Votre email sera communiquée à l'organisateur.rice
        </SmallText>
      );
    }
  } else {
    return (
      <div>
        <a href={routes.logIn}>Je me connecte</a> ou{" "}
        <a href={routes.signIn}>je m'inscris</a> pour participer à l'événement
      </div>
    );
  }
};

const EventHeader = ({
  name,
  rsvp,
  options,
  startTime,
  routes,
  isOrganizer,
  hasSubscriptionForm,
}) => {
  const config = useGlobalContext();
  const logged = config.user !== null;
  const rsvped = !!rsvp;
  const now = DateTime.local();
  const past = now > startTime;
  let eventString = startTime.toLocaleString(dateFormat);
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
  startTime: PropTypes.instanceOf(DateTime),
  hasSubscriptionForm: PropTypes.bool,
  isOrganizer: PropTypes.bool,
  options: PropTypes.shape({
    price: PropTypes.string,
  }),
  rsvp: PropTypes.shape({ status: PropTypes.string }),
  routes: PropTypes.shape({
    page: PropTypes.string,
    join: PropTypes.string,
    cancel: PropTypes.string,
  }),
};

export default EventHeader;
