import PropTypes from "prop-types";
import React from "react";

import { DateTime, Interval } from "luxon";

import { routeConfig } from "@agir/front/app/routes.config";

import Card from "./Card";
import FeatherIcon from "./FeatherIcon";
import { displayIntervalStart } from "@agir/lib/utils/time";
import { Column, Hide, Row } from "@agir/front/genericComponents/grid";
import style from "@agir/front/genericComponents/_variables.scss";
import styled from "styled-components";
import Button from "@agir/front/genericComponents/Button";
import CSRFProtectedForm from "@agir/front/genericComponents/CSRFProtectedForm";
import { useHistory } from "react-router-dom";

const RSVPButton = ({ id, hasSubscriptionForm, rsvp, routes, schedule }) => {
  if (schedule.isBefore(DateTime.local())) {
    return null;
  }

  if (rsvp) {
    return (
      <Button
        as="Link"
        small
        color="confirmed"
        icon="check"
        to={
          routeConfig.eventDetails
            ? routeConfig.eventDetails.getLink({ eventPk: id })
            : routes.details
        }
      >
        Je participe
      </Button>
    );
  }

  if (hasSubscriptionForm) {
    return (
      <Button small as="a" color="primary" href={routes.rsvp}>
        Participer
      </Button>
    );
  }

  return (
    <CSRFProtectedForm
      method="post"
      action={routes.rsvp}
      style={{ display: "inline-block" }}
    >
      <Button small type="submit" color="primary" icon="calendar">
        Participer
      </Button>
    </CSRFProtectedForm>
  );
};

RSVPButton.propTypes = {
  id: PropTypes.string,
  hasSubscriptionForm: PropTypes.bool,
  rsvp: PropTypes.bool,
  routes: PropTypes.shape({
    details: PropTypes.string,
    rsvp: PropTypes.string,
  }),
  schedule: PropTypes.instanceOf(Interval),
};

const Buttons = styled.div`
  display: flex;

  * + ${Button} {
    margin-left: 0.5rem;
  }
`;
const Illustration = styled.div`
  margin: -1.5rem -1.5rem 1.5rem;
  text-align: center;
  background-color: ${style.black50};
  @media only screen and (max-width: ${style.collapse}px) {
    margin: -1rem -1rem 1rem;
  }
  img {
    max-height: 200px;
  }
`;

const EventCard = (props) => {
  const {
    id,
    illustration,
    hasSubscriptionForm,
    schedule,
    location,
    name,
    participantCount,
    rsvp,
    routes,
    groups,
    compteRendu,
  } = props;
  const history = useHistory();
  const handleClick = React.useCallback(
    (e) => {
      if (["A", "BUTTON"].includes(e.target.tagName.toUpperCase())) {
        return;
      }
      id &&
        routeConfig.eventDetails &&
        history.push(routeConfig.eventDetails.getLink({ eventPk: id }));
    },
    [history, id]
  );

  return (
    <Card onClick={handleClick}>
      <Illustration>
        {illustration && <img src={illustration} alt="Image d'illustration" />}
      </Illustration>
      <header style={{ marginBottom: 20 }}>
        <p
          style={{
            fontSize: "14px",
            color: schedule.isBefore(DateTime.local())
              ? style.black500
              : style.primary500,
            fontWeight: 500,
          }}
        >
          {displayIntervalStart(schedule)}
          {location && location.shortLocation && (
            <> • {location.shortLocation}</>
          )}
        </p>
        <h3
          style={{
            fontWeight: 700,
            fontSize: "1rem",
            marginTop: 0,
            marginBottom: "0.4rem",
          }}
        >
          {name}
        </h3>
        {Array.isArray(groups) && groups.length > 0
          ? groups.map((group) => (
              <p
                key={group.name}
                style={{
                  fontWeight: "500",
                  fontSize: "14px",
                  lineHeight: "1",
                  color: style.black500,
                }}
              >
                {group.name}
              </p>
            ))
          : null}
      </header>
      <Row style={{ fontSize: "14px" }}>
        <Column grow collapse={0}>
          <Buttons>
            <RSVPButton
              id={id}
              hasSubscriptionForm={hasSubscriptionForm}
              rsvp={!!rsvp}
              routes={routes}
              schedule={schedule}
            />
            {compteRendu ? (
              <Button
                small
                color="tertiary"
                icon="file-text"
                as="Link"
                to={
                  routeConfig.eventDetails
                    ? routeConfig.eventDetails.getLink({ eventPk: id })
                    : routes.details
                }
              >
                Voir le compte-rendu
              </Button>
            ) : null}
            <Button
              small
              as="Link"
              to={
                routeConfig.eventDetails
                  ? routeConfig.eventDetails.getLink({ eventPk: id })
                  : routes.details
              }
            >
              Détails
            </Button>
          </Buttons>
        </Column>
        {participantCount > 1 && (
          <Column
            collapse={0}
            style={{ paddingTop: "0.5rem", alignSelf: "flex-end" }}
          >
            {participantCount}{" "}
            <Hide as="span" under={400}>
              participant⋅es
            </Hide>
            <Hide as="span" over={401}>
              <FeatherIcon inline small name="user" />
            </Hide>
          </Column>
        )}
      </Row>
    </Card>
  );
};

EventCard.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  participantCount: PropTypes.number,
  hasSubscriptionForm: PropTypes.bool,
  illustration: PropTypes.string,
  schedule: PropTypes.instanceOf(Interval).isRequired,
  location: PropTypes.shape({
    name: PropTypes.string,
    address: PropTypes.string,
    shortLocation: PropTypes.string,
  }),
  rsvp: PropTypes.string,
  routes: PropTypes.shape({
    details: PropTypes.string,
    join: PropTypes.string,
    cancel: PropTypes.string,
    compteRendu: PropTypes.string,
  }),
  groups: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      name: PropTypes.string,
    })
  ),
  compteRendu: PropTypes.string,
};

export default EventCard;
