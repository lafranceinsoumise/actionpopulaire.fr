import { DateTime, Interval } from "luxon";
import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import { useLocation } from "react-router-dom";
import { mutate } from "swr";
import styled from "styled-components";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getIsConnected, getRoutes } from "@agir/front/globalContext/reducers";
import * as api from "@agir/events/common/api";

import style from "@agir/front/genericComponents/_variables.scss";
import Button from "@agir/front/genericComponents/Button";
import Link from "@agir/front/app/Link";
import { Hide } from "@agir/front/genericComponents/grid";
import Popin from "@agir/front/genericComponents/Popin";

import { displayHumanDate, displayIntervalEnd } from "@agir/lib/utils/time";
import { routeConfig } from "@agir/front/app/routes.config";

import JoiningDetails from "./JoiningDetails";
import AddGroupAttendee from "./AddGroupAttendee";
import ButtonMenu from "@agir/front/genericComponents/ButtonMenu";
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

const StyledButtonMenu = styled(ButtonMenu)``;

const StyledActions = styled.div`
  display: flex;
  flex-wrap: wrap;
  margin-bottom: 1rem;
  margin-top: 1rem;

  > ${Button}, > ${StyledButtonMenu} {
    margin-right: 0.5rem;
    margin-bottom: 0.5rem;
  }

  @media (max-width: ${style.collapse}px) {
    > ${Button} {
      width: 100%;
      margin-bottom: 0.5rem;
    }
    ${StyledButtonMenu} {
      width: 100%;
      margin-bottom: 0.5rem;
    }
  }
`;

const Actions = (props) => {
  const {
    id,
    past,
    rsvped,
    logged,
    isManager,
    routes,
    hasPrice,
    allowGuests,
    hasSubscriptionForm,
    groups,
    groupsAttendees,
    backLink,
  } = props;

  const [isLoading, setIsLoading] = useState(false);

  const [showQuitEvent, setShowQuitEvent] = useState(false);

  const handleQuitEvent = (e) => {
    e.preventDefault();
    setShowQuitEvent(true);
  };

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

  if (past) {
    return (
      <StyledActions>
        <Button disabled color="unavailable">
          Événement terminé
        </Button>
        {isManager && (
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

  return (
    <>
      <StyledActions>
        {isManager && (
          <Button
            icon="settings"
            link
            to={routeConfig.eventSettings.getLink({ eventPk: id })}
            color="primary"
          >
            Gérer l'événement
          </Button>
        )}
        {!rsvped ? (
          <Button
            type="submit"
            color="primary"
            loading={isLoading}
            disabled={isLoading}
            onClick={handleRSVP}
          >
            Participer à l'événement
          </Button>
        ) : (
          !hasPrice && (
            <>
              <StyledButtonMenu
                color="success"
                icon="check-circle"
                text="Je participe"
                shouldDismissOnClick
                MobileLayout={Popin}
              >
                <a href="" onClick={handleQuitEvent}>
                  Annuler
                </a>
              </StyledButtonMenu>
              <QuitEventButton
                eventPk={id}
                isOpen={showQuitEvent}
                setIsOpen={setShowQuitEvent}
              />
            </>
          )
        )}
        <AddGroupAttendee
          id={id}
          groups={groups}
          groupsAttendees={groupsAttendees}
        />
        {allowGuests && (hasSubscriptionForm || hasPrice) && (
          <Button link href={routes.rsvp}>
            Ajouter une personne
          </Button>
        )}
      </StyledActions>
      <JoiningDetails
        id={id}
        hasPrice={hasPrice}
        rsvped={rsvped}
        groups={groupsAttendees}
        logged={logged}
        backLink={backLink}
      />
    </>
  );
};
Actions.propTypes = {
  id: PropTypes.string,
  name: PropTypes.string,
  hasSubscriptionForm: PropTypes.bool,
  hasPrice: PropTypes.bool,
  past: PropTypes.bool,
  rsvped: PropTypes.bool,
  logged: PropTypes.bool,
  isManager: PropTypes.bool,
  allowGuests: PropTypes.bool,
  routes: PropTypes.shape({
    manage: PropTypes.string,
    rsvp: PropTypes.string,
  }),
  groups: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string,
      isManager: PropTypes.bool,
    })
  ),
  groupsAttendees: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string,
      isManager: PropTypes.bool,
    })
  ),
  backLink: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
};

const AdditionalMessage = ({ isOrganizer, logged, rsvped, price }) => {
  const location = useLocation();

  if (!logged) {
    return (
      <div>
        <ActionLink
          route="login"
          state={{ from: "event", next: location.pathname }}
        >
          Je me connecte
        </ActionLink>{" "}
        ou{" "}
        <ActionLink
          route="signup"
          state={{ from: "event", next: location.pathname }}
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

const EventHeader = (props) => {
  const {
    id,
    name,
    rsvp,
    options,
    schedule,
    routes,
    isOrganizer,
    isManager,
    allowGuests,
    hasSubscriptionForm,
    groups,
    groupsAttendees,
    backLink,
  } = props;

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
        isManager={isManager}
        hasPrice={!!options && !!options.price}
        allowGuests={allowGuests}
        hasSubscriptionForm={hasSubscriptionForm}
        groups={groups}
        groupsAttendees={groupsAttendees}
        backLink={backLink}
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
  startTime: PropTypes.instanceOf(DateTime),
  endTime: PropTypes.instanceOf(DateTime),
  schedule: PropTypes.instanceOf(Interval),
  hasSubscriptionForm: PropTypes.bool,
  isOrganizer: PropTypes.bool,
  isManager: PropTypes.bool,
  options: PropTypes.shape({
    price: PropTypes.string,
  }),
  rsvp: PropTypes.string,
  routes: PropTypes.object,
  allowGuests: PropTypes.bool,
  groups: PropTypes.array,
  groupsAttendees: PropTypes.array,
  backLink: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
};

export default EventHeader;
