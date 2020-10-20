import React from "react";
import PropTypes from "prop-types";
import EventHeader from "./EventHeader";
import EventLocation from "./EventLocation";
import FacebookLink from "./FacebookLink";
import Description from "./Description";
import { DateTime } from "luxon";
import {
  Column,
  Container,
  GrayBackground,
  ResponsiveLayout,
  Row,
} from "@agir/front/genericComponents/grid";
import Contact from "@agir/front/genericComponents/Contact";
import EventInfo from "@agir/events/eventPage/EventInfo";
import Share from "@agir/front/genericComponents/Share";
import Card from "@agir/front/genericComponents/Card";
import GroupCard from "@agir/events/eventPage/GroupCard";

const MobileLayout = (props) => {
  return (
    <Container>
      <Row>
        <Column>
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
          <EventLocation {...props} />
          <Contact {...props} />
          <Card>
            <Description {...props} />
          </Card>
          <Contact {...props} />
          <FacebookLink {...props} />
          <Share />
          <GroupCard {...props.group} />
        </Column>
      </Row>
    </Container>
  );
};

const DesktopLayout = (props) => {
  return (
    <GrayBackground>
      <Container>
        <Row>
          <Column fill>
            <div style={{ margin: "0 -1000px" }}>
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
            <Description {...props} />
            <GroupCard {...props.group} />
          </Column>
          <Column width="380px" style={{ paddingTop: "24px" }}>
            <EventLocation {...props} />
            <Contact {...props} />
            <EventInfo {...props} />
            <FacebookLink {...props} />
            <Share />
          </Column>
        </Row>
      </Container>
    </GrayBackground>
  );
};

const EventPage = (props) => {
  props = {
    ...props,
    startTime: DateTime.fromISO(props.startTime).setLocale("fr"),
    endTime: DateTime.fromISO(props.endTime).setLocale("fr"),
  };

  return (
    <ResponsiveLayout
      desktop={<DesktopLayout {...props} />}
      mobile={<MobileLayout {...props} />}
    />
  );
};

EventPage.propTypes = {
  id: PropTypes.string,
  name: PropTypes.string,
  compteRendu: PropTypes.string,
  compteRenduPhotos: PropTypes.arrayOf(PropTypes.string),
  illustration: PropTypes.string,
  description: PropTypes.string,
  startTime: PropTypes.string,
  endTime: PropTypes.string,
  location: PropTypes.shape({
    name: PropTypes.string,
    address: PropTypes.string,
  }),
  group: PropTypes.objectOf(PropTypes.string),
  routes: PropTypes.shape({
    page: PropTypes.string,
    map: PropTypes.string,
    join: PropTypes.string,
    cancel: PropTypes.string,
    manage: PropTypes.string,
    calendarExport: PropTypes.string,
    googleExport: PropTypes.string,
    outlookExport: PropTypes.string,
    facebook: PropTypes.string,
  }),
};

MobileLayout.propTypes = EventPage.propTypes;
DesktopLayout.propTypes = EventPage.propTypes;

export default EventPage;
