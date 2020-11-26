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
import { dateFromISOString, displayHumanDay } from "@agir/lib/utils/time";
import FilterTabs from "@agir/front/genericComponents/FilterTabs";

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
      color: ${style.black1000};
    }
    a {
      font-weight: bold;
      cursor: pointer;
    }
  }
`;

const StyledAgenda = styled.div`
  & header {
    margin-bottom: 32px;
  }

  & h2 {
    font-size: 18px;
    font-weight: 500;
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

const OtherEvents = ({ others }) => {
  const { routes, user } = useGlobalContext();
  const NEAR_TYPE = "À proximité";
  const GROUPS_TYPE = "Dans mes groupes";
  const PAST_TYPE = "Passés";
  const ORGANIZED_TYPE = "Organisés";

  const types = React.useMemo(
    () =>
      others[0].distance !== null
        ? [NEAR_TYPE, GROUPS_TYPE, PAST_TYPE, ORGANIZED_TYPE]
        : [GROUPS_TYPE, PAST_TYPE, ORGANIZED_TYPE],
    [others]
  );

  const [typeFilter, setTypeFilter] = React.useState(0);
  let otherEventDates = React.useMemo(
    () =>
      Object.entries(
        others
          .filter((event) => {
            switch (types[typeFilter]) {
              case NEAR_TYPE:
                return event.distance < 100 * 1000 && !event.rsvp;
              case GROUPS_TYPE:
                return (
                  event.groups.filter((group) => user.groups.includes(group.id))
                    .length > 0
                );
              case PAST_TYPE:
                return dateFromISOString(event.startTime) < DateTime.local();
              case ORGANIZED_TYPE:
                return event.isOrganizer;
            }
          })
          .map((event) => ({
            ...event,
            schedule: Interval.fromDateTimes(
              dateFromISOString(event.startTime),
              dateFromISOString(event.endTime)
            ),
          }))
          .reduce((days, event) => {
            const day = displayHumanDay(dateFromISOString(event.startTime));
            (days[day] = days[day] || []).push(event);
            return days;
          }, {})
      ),
    [others, types, typeFilter, user.groups]
  );

  if ([ORGANIZED_TYPE, PAST_TYPE].includes(types[typeFilter])) {
    otherEventDates = otherEventDates
      .map(([date, events]) => [date, events.reverse()])
      .reverse();
  }

  return (
    <>
      <FilterTabs tabs={types} onTabChange={setTypeFilter} />

      {otherEventDates.length > 0 ? (
        otherEventDates.map(([date, events]) => (
          <div key={date}>
            <Day>{date}</Day>
            {events.map((event) => (
              <EventCard key={event.id} {...event} />
            ))}
          </div>
        ))
      ) : (
        <EmptyAgenda>
          <p>
            Il n'y a aucun événement à afficher avec les filtres sélectionnés.
          </p>
          <p>
            Pas d'événement prévu dans votre ville ?{" "}
            <a href={routes.createEvent}>Commencez par en créer un</a>.
          </p>
        </EmptyAgenda>
      )}
    </>
  );
};

OtherEvents.propTypes = {
  others: PropTypes.arrayOf(PropTypes.object),
};

const Agenda = ({ rsvped, others }) => {
  const { routes } = useGlobalContext();

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

  return (
    <StyledAgenda>
      <header>
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
            <Button small as="a" href={routes.eventMap} icon="map">
              Carte
            </Button>
          </div>
        </TopBar>
      </header>
      <Row>
        <Column grow>
          {rsvpedEvents.length > 0 && (
            <>
              <h2>Mes événements</h2>
              {rsvpedEvents.map((event) => (
                <EventCard key={event.id} {...event} />
              ))}
              <h2>Autres événements près de chez moi</h2>
            </>
          )}
          <OtherEvents others={others} />
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
  others: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      startTime: PropTypes.string,
      endTime: PropTypes.string,
    })
  ),
};
