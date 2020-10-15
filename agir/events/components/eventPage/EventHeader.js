import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import { DateTime } from "luxon";

import Button from "@agir/front/genericComponents/Button";
import { useConfig } from "@agir/front/genericComponents/Config";
import style from "@agir/front/genericComponents/style.scss";

const dateFormat = {
  weekday: "long",
  month: "long",
  day: "numeric",
  hour: "numeric",
  minute: "2-digit",
};

const EventHeaderContainer = styled.div`
  margin: 3.825rem auto 3.825rem 10.7rem;

  * {
    margin: 0.5rem 0;
  }
`;

const EventTitle = styled.h1`
  font-size: 1.75rem/1.4;
  font-weight: 800;
  margin-bottom: 0.5rem;

  a,
  a:hover {
    text-decoration: none;
    color: ${(props) => style.brandBlack};
  }
`;

const EventDate = styled.div`
  margin: 0.5rem 0;
`;

const SmallText = styled.div`
  font-size: 0.81rem;
  font-color: ${style.gray};
`;

const RSVPButton = ({ past, rsvped, logged, routes }) => {
  if (past) {
    return <Button color="unavailable">Événement terminé</Button>;
  }

  if (logged) {
    if (rsvped) {
      return (
        <Button icon="check-circle" color="confirmed">
          Je participe
        </Button>
      );
    } else {
      return (
        <Button as="a" color="secondary" href={routes.join}>
          Participer à l'événement
        </Button>
      );
    }
  } else {
    return (
      <Button color="secondary" disabled={true}>
        Participer à l'événement
      </Button>
    );
  }
};
RSVPButton.propTypes = {
  logged: PropTypes.bool,
  rsvped: PropTypes.bool,
};

const EventHeader = ({ name, date, rsvped, routes }) => {
  const config = useConfig();
  const logged = config.user !== null;
  const eventDate = DateTime.fromISO(date).setLocale("fr");
  const now = DateTime.local();
  const past = now > eventDate;
  let eventString = eventDate.toLocaleString(dateFormat);
  eventString = eventString.slice(0, 1).toUpperCase() + eventString.slice(1);

  return (
    <EventHeaderContainer>
      <EventTitle>
        <a href={routes.page}>{name}</a>
      </EventTitle>
      <EventDate>{eventString}</EventDate>
      <RSVPButton past={past} logged={logged} rsvped={rsvped} routes={routes} />
      {logged ? (
        rsvped ? (
          <SmallText>
            <a href={routes.cancel}>Annuler ma participation</a>
          </SmallText>
        ) : (
          <SmallText>
            Votre email sera communiquée à l'organisateur.rice
          </SmallText>
        )
      ) : (
        <div>
          <a href={config.routes.logIn}>Je me connecte</a> ou{" "}
          <a href={config.routes.signIn}>je m'inscris</a> pour participer à
          l'événement
        </div>
      )}
    </EventHeaderContainer>
  );
};

EventHeader.propTypes = {
  name: PropTypes.string,
  date: PropTypes.string,
  rsvped: PropTypes.bool,
  routes: PropTypes.shape({
    page: PropTypes.string,
    join: PropTypes.string,
    cancel: PropTypes.string,
  }),
};

export default EventHeader;
