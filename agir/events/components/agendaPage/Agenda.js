import React from "react";
import Button from "@agir/front/genericComponents/Button";
import styled from "styled-components";
import { Column } from "@agir/front/genericComponents/grid";
import { Row } from "@agir/donations/donationForm/AllocationsWidget/Styles";

import styles from "@agir/front/genericComponents/style.scss";
import { DateTime, Interval } from "luxon";
import EventCard from "@agir/front/genericComponents/EventCard";
import PropTypes from "prop-types";
import { displayHumanDay } from "@agir/lib/utils/time";

const StyledAgenda = styled.div`
  & h2 {
    font-size: 18px;
  }
`;

const Banner = styled.div`
  @media only screen and (min-width: ${styles.collapse}px) {
    display: none;
  }

  margin: 0 -16px 24px;
  height: 10rem;
  padding: 32px 200px 0 40px;
  font-size: 29px;
  & h1 {
    color: #fff;
  }

  background-image: url(https://picsum.photos/992/500);
`;

const TopBar = styled.div`
  display: flex;
  flex-direction: row;
  margin-bottom: 24px;

  & > h1 {
    @media only screen and (max-width: ${styles.collapse}px) {
      display: none;
    }
    margin: 0 1.5rem 0 0;
    font-size: 28px;
  }

  & > ${Button} {
    margin-right: 0.5rem;
  }
`;

const Day = styled.h3`
  color: ${styles.black500};
  text-transform: uppercase;
  font-size: 14px;
  margin-top: 24px;
`;

const Agenda = ({ rsvped, suggested }) => (
  <StyledAgenda>
    <header>
      <Banner>
        <h1>Bonjour</h1>
      </Banner>
      <TopBar>
        <h1>Agenda</h1>
        <Button small as="a" color={"secondary"} href="#" icon="plus">
          Créer un évenement
        </Button>
        <Button small as="a" href="#" icon="map">
          Carte
        </Button>
      </TopBar>
    </header>
    {rsvped.length > 0 && (
      <Row>
        <Column grow>
          <h2>Mes événements</h2>
          {rsvped.map(({ startTime, endTime, ...props }) => {
            props = {
              ...props,
              schedule: Interval.fromDateTimes(
                DateTime.fromISO(startTime).setLocale("fr"),
                DateTime.fromISO(endTime).setLocale("fr")
              ),
            };
            return <EventCard key={props.id} {...props} />;
          })}
        </Column>
      </Row>
    )}
    {suggested.length > 0 && (
      <Row>
        <Column grow>
          <h2>Les événements près de chez moi</h2>
          {Object.entries(
            suggested.reduce((days, event) => {
              const day = displayHumanDay(DateTime.fromISO(event.startTime));
              (days[day] = days[day] || []).push(event);
              return days;
            }, {})
          ).map(([day, events]) => (
            <div key={day}>
              <Day>{day}</Day>
              {events.map(({ startTime, endTime, ...props }) => {
                props = {
                  ...props,
                  schedule: Interval.fromDateTimes(
                    DateTime.fromISO(startTime).setLocale("fr"),
                    DateTime.fromISO(endTime).setLocale("fr")
                  ),
                };
                return <EventCard key={props.id} {...props} />;
              })}
            </div>
          ))}
        </Column>
      </Row>
    )}
  </StyledAgenda>
);
export default Agenda;

Agenda.propTypes = {
  rsvped: PropTypes.array,
  suggested: PropTypes.array,
};
