import PropTypes from "prop-types";
import Card from "./Card";
import React from "react";
import FeatherIcon from "./FeatherIcon";
import { Interval } from "luxon";
import { displayInterval } from "@agir/lib/utils/time";
import { Column, Hide, Row } from "@agir/front/genericComponents/grid";
import styles from "@agir/front/genericComponents/style.scss";
import styled from "styled-components";
import Button from "@agir/front/genericComponents/Button";
import CSRFProtectedForm from "@agir/front/genericComponents/CSRFProtectedForm";

const RSVPButton = ({ hasSubscriptionForm, rsvp, routes }) => {
  if (rsvp) {
    return (
      <Button as="a" small color="confirmed" icon="check" href={routes.cancel}>
        Je participe
      </Button>
    );
  }

  if (hasSubscriptionForm) {
    return (
      <Button small as="a" color="secondary" href={routes.join}>
        Participer
      </Button>
    );
  }

  return (
    <CSRFProtectedForm
      method="post"
      action={routes.join}
      style={{ display: "inline-block" }}
    >
      <Button small type="submit" color="secondary" icon="calendar">
        Participer
      </Button>
    </CSRFProtectedForm>
  );
};

RSVPButton.propTypes = {
  hasSubscriptionForm: PropTypes.bool,
  rsvp: PropTypes.bool,
  routes: PropTypes.shape({ cancel: PropTypes.string, join: PropTypes.string }),
};

const Illustration = styled.img`
  max-height: 200px;

  @media only screen and (min-width: ${styles.collapse}px) {
    max-height: 360px;
  }
`;

const EventCard = ({
  illustration,
  hasSubscriptionForm,
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
      {illustration && (
        <Illustration src={illustration} alt="Image d'illustration" />
      )}
    </div>
    <p style={{ fontSize: "14px", color: styles.primary500, fontWeight: 600 }}>
      {displayInterval(schedule)}
      {location && location.shortAddress && <> • {location.shortAddress}</>}
    </p>
    <h3 style={{ fontWeight: 700 }}>{name}</h3>
    <Row style={{ fontSize: "14px" }}>
      <Column grow collapse={0}>
        <RSVPButton
          hasSubscriptionForm={hasSubscriptionForm}
          rsvp={!!rsvp}
          routes={routes}
        />
        <Button
          small
          as="a"
          href={routes.details}
          style={{ marginLeft: "8px" }}
        >
          Details
        </Button>
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
  hasSubscriptionForm: PropTypes.bool,
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
