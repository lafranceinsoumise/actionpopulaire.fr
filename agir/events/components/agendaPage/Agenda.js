import { DateTime, Interval } from "luxon";
import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { Row } from "@agir/donations/donationForm/AllocationsWidget/Styles";
import { Column } from "@agir/front/genericComponents/grid";
import Button from "@agir/front/genericComponents/Button";
import EventCard from "@agir/front/genericComponents/EventCard";

import { useGlobalContext } from "@agir/front/genericComponents/GlobalContext";
import { displayHumanDay } from "@agir/lib/utils/time";

const Banner = styled.h1`
  display: flex;
  flex-flow: column nowrap;
  align-items: stretch;
  justify-content: center;
  margin: 0;
  padding: 0 25px;
  height: 10rem;
  font-size: 29px;
  color: #fff;
  background-image: url(https://picsum.photos/992/500);
  background-repeat: no-repeat;
  background-size: cover;
  background-position: center center;

  @media only screen and (min-width: ${style.collapse}px) {
    display: none;
  }
`;

const TopBar = styled.div`
  display: flex;
  flex-direction: row;
  margin-bottom: 24px;
  justify-content: space-between;

  & > h1 {
    @media only screen and (max-width: ${style.collapse}px) {
      display: none;
    }
    margin: 0 1.5rem 0 0;
    font-size: 28px;
  }

  & > div {
    display: flex;
    flex-direction: row-reverse;
    align-items: center;

    @media only screen and (max-width: ${style.collapse}px) {
      flex-direction: row;
    }
  }

  & ${Button} + ${Button} {
    @media only screen and (min-width: ${style.collapse}px) {
      margin-right: 0.5rem;
    }
    @media only screen and (max-width: ${style.collapse}px) {
      margin-left: 0.5rem;
    }
  }
`;

const Day = styled.h3`
  color: ${style.black500};
  text-transform: uppercase;
  font-size: 14px;
  margin-top: 24px;
`;

const EmptyAgenda = styled.div`
  & p {
    strong {
      color: ${style.primary500};
    }
    a {
      color: ${style.secondary500};
      font-weight: bold;
      cursor: pointer;
    }
  }
`;

const StyledAgenda = styled.div`
  & h2 {
    font-size: 18px;
  }

  & h2,
  & ${Day}, & ${EmptyAgenda} {
    margin: 20px 0;

    @media (max-width: ${style.collapse}px) {
      margin: 20px 25px;
    }
  }
  & ${TopBar} {
    margin: 0;

    @media (max-width: ${style.collapse}px) {
      margin: 20px 25px;
    }
  }
`;

const Agenda = ({ rsvped, suggested }) => {
  const { routes, user } = useGlobalContext();

  const rsvpedEvents = React.useMemo(
    () =>
      rsvped.map((event) => ({
        ...event,
        schedule: Interval.fromDateTimes(
          DateTime.fromISO(event.startTime).setLocale("fr"),
          DateTime.fromISO(event.endTime).setLocale("fr")
        ),
      })),
    [rsvped]
  );
  const suggestedEventDates = React.useMemo(
    () =>
      Object.entries(
        suggested
          .map((event) => ({
            ...event,
            schedule: Interval.fromDateTimes(
              DateTime.fromISO(event.startTime).setLocale("fr"),
              DateTime.fromISO(event.endTime).setLocale("fr")
            ),
          }))
          .reduce((days, event) => {
            const day = displayHumanDay(
              DateTime.fromISO(event.startTime).setLocale("fr")
            );
            (days[day] = days[day] || []).push(event);
            return days;
          }, {})
      ),
    [suggested]
  );

  return (
    <StyledAgenda>
      <header>
        <Banner>
          <span>Bonjour</span>
          <span>{user && user.firstName}</span>
        </Banner>
        <TopBar>
          <h1>Événements</h1>
          <div>
            <Button
              small
              as="a"
              color="secondary"
              href={routes.createEvent}
              icon="plus"
            >
              Créer un évenement
            </Button>
            <Button
              small
              as="a"
              href={routes.eventMap}
              icon="map"
              color="white"
            >
              Carte
            </Button>
          </div>
        </TopBar>
      </header>
      <Row>
        <Column grow>
          {rsvped.length === 0 && suggested.length === 0 ? (
            <EmptyAgenda>
              <p>
                <strong>Oups, il n'y a rien à afficher&nbsp;!</strong>
              </p>
              <p>
                Il n'y a aucun événement à afficher avec les filtres
                sélectionnés.
              </p>
              <p>
                Pas d'événement prévu dans votre ville ?{" "}
                <a href={routes.createEvent}>Commencez par en créer un</a>.
              </p>
            </EmptyAgenda>
          ) : null}
          {rsvpedEvents.length > 0 && (
            <>
              <h2>Mes événements</h2>
              {rsvpedEvents.map((event) => (
                <EventCard key={event.id} {...event} />
              ))}
            </>
          )}
          {suggestedEventDates.length > 0 && (
            <>
              <h2>Les événements près de chez moi</h2>
              {suggestedEventDates.map(([date, events]) => (
                <div key={date}>
                  <Day>{date}</Day>
                  {events.map((event) => (
                    <EventCard key={event.id} {...event} />
                  ))}
                </div>
              ))}
            </>
          )}
        </Column>
      </Row>
    </StyledAgenda>
  );
};
export default Agenda;

Agenda.propTypes = {
  rsvped: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      startTime: PropTypes.string,
      endTime: PropTypes.string,
    })
  ),
  suggested: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      startTime: PropTypes.string,
      endTime: PropTypes.string,
    })
  ),
};
