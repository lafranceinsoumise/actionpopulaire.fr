import React from "react";
import PropTypes from "prop-types";
import EventHeader from "./EventHeader";
import EventLocationCard from "./EventLocationCard";
import EventFacebookLinkCard from "./EventFacebookLinkCard";
import EventDescription from "./EventDescription";
import { DateTime, Interval } from "luxon";
import {
  Column,
  Container,
  GrayBackground,
  ResponsiveLayout,
  Row,
} from "@agir/front/genericComponents/grid";
import ContactCard from "@agir/front/genericComponents/ContactCard";
import EventInfoCard from "@agir/events/eventPage/EventInfoCard";
import ShareCard from "@agir/front/genericComponents/ShareCard";
import Card from "@agir/front/genericComponents/Card";
import EventGroupCard from "@agir/events/eventPage/EventGroupCard";

const MobileLayout = (props) => {
  return (
    <Container>
      <Row>
        <Column stack>
          {props.illustration && (
            <div
              style={{
                margin: "0 -16px",
              }}
            >
              <img
                src={props.illustration}
                alt="Image d'illustration de l'événement postée par l'utilisateur"
                style={{
                  width: "100%",
                  height: "auto",
                }}
              />
            </div>
          )}
          <Card>
            <EventHeader {...props} />
          </Card>
          <EventLocationCard {...props} />
          {(props.participantCount > 1 || props.groups.length > 0) && (
            <EventInfoCard {...props} />
          )}
          <Card>
            <EventDescription {...props} />
          </Card>
          {props.contact && <ContactCard {...props.contact} />}
          {props.routes.facebook && <EventFacebookLinkCard {...props} />}
          <ShareCard />
          {props.groups.length > 0 &&
            props.groups.map((group, key) => (
              <EventGroupCard key={key} {...group} />
            ))}
        </Column>
      </Row>
    </Container>
  );
};

const DesktopLayout = (props) => {
  return (
    <GrayBackground
      style={{
        overflowX: "hidden",
        minHeight: "calc(100vh + 10rem)",
        marginBottom: "-2.5rem",
        paddingBottom: "2.5rem",
      }}
    >
      <Container>
        <Row>
          <Column grow>
            <div style={{ margin: "0 -1000px 40px" }}>
              <div
                style={{
                  padding: "60px 1000px",
                  backgroundColor: "#fff",
                  boxShadow: "0px 1px 0px rgba(0, 0, 0, 0.05)",
                }}
              >
                <EventHeader {...props} />
              </div>
            </div>
            <EventDescription {...props} />
            {props.groups.length > 0 &&
              props.groups.map((group, key) => (
                <EventGroupCard key={key} {...group} />
              ))}
          </Column>
          <Column width="380px" style={{ paddingTop: "24px" }}>
            <EventLocationCard {...props} />
            {props.contact && <ContactCard {...props.contact} />}
            {(props.participantCount > 1 || props.groups.length > 0) && (
              <EventInfoCard {...props} />
            )}
            {props.routes.facebook && <EventFacebookLinkCard {...props} />}
            <ShareCard />
          </Column>
        </Row>
      </Container>
    </GrayBackground>
  );
};

const EventPage = ({ startTime, endTime, ...props }) => {
  props = {
    ...props,
    schedule: Interval.fromDateTimes(
      DateTime.fromISO(startTime).setLocale("fr"),
      DateTime.fromISO(endTime).setLocale("fr")
    ),
  };

  return (
    <ResponsiveLayout
      desktop={<DesktopLayout {...props} />}
      mobile={<MobileLayout {...props} />}
    />
  );
};

EventPage.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  hasSubscriptionForm: PropTypes.bool,
  isOrganizer: PropTypes.bool,
  rsvp: PropTypes.string,
  compteRendu: PropTypes.string,
  compteRenduPhotos: PropTypes.arrayOf(PropTypes.string),
  illustration: PropTypes.string,
  description: PropTypes.string,
  startTime: PropTypes.string.isRequired,
  endTime: PropTypes.string.isRequired,
  location: PropTypes.shape({
    name: PropTypes.string,
    address: PropTypes.string,
    shortAddress: PropTypes.string,
  }),
  participantCount: PropTypes.number.isRequired,
  contact: PropTypes.shape(ContactCard.propTypes),
  options: PropTypes.shape({ price: PropTypes.string }),
  groups: PropTypes.arrayOf(PropTypes.shape(EventGroupCard.propTypes)),
  routes: PropTypes.shape({
    page: PropTypes.string,
    map: PropTypes.string,
    join: PropTypes.string,
    cancel: PropTypes.string,
    manage: PropTypes.string,
    calendarExport: PropTypes.string,
    googleExport: PropTypes.string,
    facebook: PropTypes.string,
    addPhoto: PropTypes.string,
    compteRendu: PropTypes.string,
  }),
};

export default EventPage;
