import { DateTime, Interval } from "luxon";
import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import { useLocation } from "react-router-dom";
import styled from "styled-components";
import { mutate } from "swr";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getIsConnected, getRoutes } from "@agir/front/globalContext/reducers";
import * as api from "@agir/events/common/api";

import Button from "@agir/front/genericComponents/Button";
import Link from "@agir/front/app/Link";
import { Hide } from "@agir/front/genericComponents/grid";

import style from "@agir/front/genericComponents/_variables.scss";
import { displayHumanDate, displayIntervalEnd } from "@agir/lib/utils/time";
import { routeConfig } from "@agir/front/app/routes.config";

import QuitEventButton from "./QuitEventButton";

import logger from "@agir/lib/utils/logger";

const log = logger(__filename);

const EventHeaderContainer = styled.div`
  @media (min-width: ${style.collapse}px) {
    margin-bottom: 2rem;
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

const ActionLink = styled(Link)`
  font-weight: 700;
  text-decoration: underline;
`;
const ActionDetails = styled.div`
  margin-top: 0;
  font-size: 1rem;
  display: flex;
  align-items: center;
  flex-wrap: wrap;

  div {
    display: inline-flex;
    align-items: center;
  }
`;

const StyledActions = styled.div`
  display: inline-grid;
  grid-gap: 0.5rem;
  grid-template-columns: auto auto;
  padding: 0.5rem 0;

  @media (max-width: ${style.collapse}px) {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
`;

const RSVPButton = (props) => {
  const { id, hasPrice, routes, hasSubscriptionForm } = props;

  const [isLoading, setIsLoading] = useState(false);

  const handleRSVP = useCallback(
    async (e) => {
      e && e.preventDefault();
      setIsLoading(true);

      if (hasPrice || hasSubscriptionForm) {
        log.debug("Has price or subscription form, redirection.");
        window.location.href = routes.rsvp;
        return;
      }

      try {
        const response = await api.rsvpEvent(id);
        if (response.error) {
          log.error(response.error);
          await mutate(api.getEventEndpoint("getEvent", { eventPk: id }));
        }
      } catch (err) {
        window.location.reload();
      }

      setIsLoading(false);

      await mutate(
        api.getEventEndpoint("getEvent", { eventPk: id }),
        (event) => ({
          ...event,
          rsvped: true,
        })
      );
    },
    [id, hasPrice, routes, hasSubscriptionForm]
  );

  return (
    <StyledActions>
      <Button
        type="submit"
        color="primary"
        disabled={isLoading}
        onClick={handleRSVP}
      >
        Participer à l'événement
      </Button>
    </StyledActions>
  );
};

const Actions = (props) => {
  const {
    id,
    name,
    past,
    rsvped,
    logged,
    isOrganizer,
    routes,
    onlineUrl,
    hasPrice,
    allowGuests,
    hasSubscriptionForm,
  } = props;

  if (past) {
    return (
      <StyledActions>
        <Button disabled color="unavailable">
          Événement terminé
        </Button>
        {isOrganizer && (
          <Button
            icon="settings"
            link
            to={routeConfig.eventSettings.getLink({ eventPk: id })}
            color="primary"
          >
            Gérer l'événement
          </Button>
        )}
      </StyledActions>
    );
  }

  if (!logged) {
    return (
      <StyledActions>
        <Button color="secondary" disabled={true}>
          Participer à l'événement
        </Button>
      </StyledActions>
    );
  }

  if (rsvped) {
    return (
      <>
        <StyledActions>
          {!!onlineUrl && (
            <Button
              icon="video"
              link
              href={onlineUrl}
              target="_blank"
              color="primary"
            >
              Rejoindre en ligne
            </Button>
          )}
          {isOrganizer && (
            <Button
              icon="settings"
              link
              to={routeConfig.eventSettings.getLink({ eventPk: id })}
              color="primary"
            >
              Gérer l'événement
            </Button>
          )}
          {allowGuests && (hasSubscriptionForm || hasPrice) && (
            <Button link href={routes.rsvp}>
              Ajouter une personne
            </Button>
          )}
        </StyledActions>
        <ActionDetails>
          <div>
            <RawFeatherIcon name="check" color="green" /> &nbsp;Vous participez
            à l'évènement
          </div>
          &nbsp;&nbsp;
          {!hasPrice && <QuitEventButton id={id} name={name} />}
        </ActionDetails>
      </>
    );
  }

  return <RSVPButton {...props} />;
};
RSVPButton.propTypes = Actions.propTypes = {
  id: PropTypes.string,
  name: PropTypes.string,
  onlineUrl: PropTypes.string,
  hasSubscriptionForm: PropTypes.bool,
  hasPrice: PropTypes.bool,
  past: PropTypes.bool,
  rsvped: PropTypes.bool,
  logged: PropTypes.bool,
  isOrganizer: PropTypes.bool,
  allowGuests: PropTypes.bool,
  routes: PropTypes.shape({
    manage: PropTypes.string,
    rsvp: PropTypes.string,
  }),
};

const AdditionalMessage = ({ isOrganizer, logged, rsvped, price }) => {
  const location = useLocation();

  if (!logged) {
    return (
      <div>
        <ActionLink
          route="login"
          params={{ from: "event", next: location.pathname }}
        >
          Je me connecte
        </ActionLink>{" "}
        ou{" "}
        <ActionLink
          route="signup"
          params={{ from: "event", next: location.pathname }}
        >
          je m'inscris
        </ActionLink>{" "}
        pour participer à l'événement
      </div>
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

  if (!isOrganizer && !rsvped) {
    return (
      <SmallText>Votre email sera communiqué à l'organisateur·ice</SmallText>
    );
  }

  return <></>;
};
AdditionalMessage.propTypes = {
  id: PropTypes.string,
  name: PropTypes.string,
  hasSubscriptionForm: PropTypes.bool,
  past: PropTypes.bool,
  rsvped: PropTypes.bool,
  logged: PropTypes.bool,
  isOrganizer: PropTypes.bool,
  price: PropTypes.string,
  routes: PropTypes.object,
};

const EventHeader = ({
  id,
  name,
  rsvp,
  options,
  schedule,
  routes,
  isOrganizer,
  onlineUrl,
  allowGuests,
  hasSubscriptionForm,
}) => {
  const globalRoutes = useSelector(getRoutes);
  const logged = useSelector(getIsConnected);

  const rsvped = rsvp === "CO";
  const now = DateTime.local();
  const past = now > schedule.end;
  let eventString = displayHumanDate(schedule.start);
  eventString = eventString.slice(0, 1).toUpperCase() + eventString.slice(1);

  const pending = now >= schedule.start && now <= schedule.end;
  const eventDate = pending ? displayIntervalEnd(schedule) : eventString;

  return (
    <EventHeaderContainer>
      <EventTitle>{name}</EventTitle>
      <Hide under>
        <EventDate>{eventDate}</EventDate>
      </Hide>
      <Actions
        id={id}
        past={past}
        logged={logged}
        rsvped={rsvped}
        routes={routes}
        isOrganizer={isOrganizer}
        hasPrice={!!options && !!options.price}
        onlineUrl={onlineUrl}
        allowGuests={allowGuests}
        hasSubscriptionForm={hasSubscriptionForm}
      />
      {!past && (
        <AdditionalMessage
          id={id}
          name={name}
          isOrganizer={isOrganizer}
          past={past}
          logged={logged}
          rsvped={rsvped}
          price={options.price}
          routes={{ ...routes, ...globalRoutes }}
        />
      )}
    </EventHeaderContainer>
  );
};

EventHeader.propTypes = {
  id: PropTypes.string,
  name: PropTypes.string,
  onlineUrl: PropTypes.string,
  startTime: PropTypes.instanceOf(DateTime),
  endTime: PropTypes.instanceOf(DateTime),
  schedule: PropTypes.instanceOf(Interval),
  hasSubscriptionForm: PropTypes.bool,
  isOrganizer: PropTypes.bool,
  options: PropTypes.shape({
    price: PropTypes.string,
  }),
  rsvp: PropTypes.string,
  routes: PropTypes.object,
  allowGuests: PropTypes.bool,
};

export default EventHeader;
