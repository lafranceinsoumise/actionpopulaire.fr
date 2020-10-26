import PropTypes from "prop-types";
import Card from "./Card";
import React from "react";
import FeatherIcon from "./FeatherIcon";
import { Interval } from "luxon";
import { displayInterval } from "@agir/lib/utils/time";
import { Column, Hide, Row } from "@agir/front/genericComponents/grid";
import styles from "@agir/front/genericComponents/style.scss";
import styled from "styled-components";

const InlineButton = styled.a`
  font-size: 14px;
  text-transform: uppercase;
  font-weight: 700;

  color: ${({ color }) => color};
  &:hover {
    color: ${({ color }) => color};
  }
`;

const RSVPButton = ({ rsvp, routes }) => (
  <InlineButton
    color={rsvp ? styles.green500 : styles.secondary500}
    a={rsvp ? routes.cancel : routes.join}
  >
    {rsvp ? (
      <>
        <FeatherIcon name="check" inline small />
        Je participe
      </>
    ) : (
      <>
        <FeatherIcon name="calendar" inline small /> Participer
      </>
    )}
  </InlineButton>
);

const Illustration = styled.img`
  max-height: 200px;

  @media only screen and (min-width: ${styles.collapse}px) {
    max-height: 360px;
  }
`;

const EventCard = ({
  illustration,
  schedule,
  location,
  name,
  participantCount,
  rsvp,
  routes,
}) => (
  <Card>
    <div
      style={{
        margin: "-1.5em -1.5em 1.5em",
        textAlign: "center",
        backgroundColor: styles.black50,
      }}
    >
      <Illustration src={illustration} alt="Image d'illustration" />
    </div>
    <p style={{ fontSize: "14px" }}>
      <FeatherIcon name="clock" inline small /> {displayInterval(schedule)}
      {location && location.shortAddress && <> • {location.shortAddress}</>}
    </p>
    <h3 style={{ fontWeight: 700 }}>{name}</h3>
    <Row style={{ fontSize: "14px" }}>
      <Column fill collapse={0}>
        <RSVPButton {...{ rsvp, routes }} />
      </Column>
      {participantCount > 1 && (
        <Column collapse={0}>
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

EventCard.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  participantCount: PropTypes.number.isRequired,
  illustration: PropTypes.string,
  schedule: PropTypes.instanceOf(Interval).isRequired,
  location: PropTypes.shape({
    name: PropTypes.string,
    address: PropTypes.string,
    shortAddress: PropTypes.string,
  }),
  rsvp: PropTypes.string,
  routes: PropTypes.shape({
    details: PropTypes.string,
    join: PropTypes.string,
    cancel: PropTypes.string,
    compteRendu: PropTypes.string,
  }),
};

export default EventCard;
