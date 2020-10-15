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
  * {
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
  font-color: ${style.gray};
`;

const ResponsiveButton = styled(Button)`
  @media only screen and (max-width: 500px) {
    display: block;
  }
`;

const RSVPButton = ({ past, rsvped, logged, routes }) => {
  if (past) {
    return <Button color="unavailable">Événement terminé</Button>;
  }

  if (logged) {
    if (rsvped) {
      return (
        <ResponsiveButton icon="check-circle" color="confirmed">
          Je participe
        </ResponsiveButton>
      );
    } else {
      return (
        <ResponsiveButton as="a" color="secondary" href={routes.join}>
          Participer à l'événement
        </ResponsiveButton>
      );
    }
  } else {
    return (
      <ResponsiveButton color="secondary" disabled={true}>
        Participer à l'événement
      </ResponsiveButton>
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
  const now = DateTime.local();
  const past = now > date;
  let eventString = date.toLocaleString(dateFormat);
  eventString = eventString.slice(0, 1).toUpperCase() + eventString.slice(1);

  return (
    <EventHeaderContainer>
      <EventTitle>{name}</EventTitle>
      <EventDate>{eventString}</EventDate>
      <RSVPButton past={past} logged={logged} rsvped={rsvped} routes={routes} />
      {!past &&
        (logged ? (
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
        ))}
    </EventHeaderContainer>
  );
};

EventHeader.propTypes = {
  name: PropTypes.string,
  date: PropTypes.instanceOf(DateTime),
  rsvped: PropTypes.bool,
  routes: PropTypes.shape({
    page: PropTypes.string,
    join: PropTypes.string,
    cancel: PropTypes.string,
  }),
};

export default EventHeader;
