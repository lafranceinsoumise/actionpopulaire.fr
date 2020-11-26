import { DateTime, Interval } from "luxon";
import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import EventHeader from "./EventHeader";
import EventLocationCard from "./EventLocationCard";
import EventFacebookLinkCard from "./EventFacebookLinkCard";
import EventDescription from "./EventDescription";
import {
  Column,
  Container,
  ResponsiveLayout,
  Row,
} from "@agir/front/genericComponents/grid";
import ContactCard from "@agir/front/genericComponents/ContactCard";
import EventInfoCard from "@agir/events/eventPage/EventInfoCard";
import ShareCard from "@agir/front/genericComponents/ShareCard";
import Card from "@agir/front/genericComponents/Card";
import GroupCard from "@agir/groups/groupComponents/GroupCard";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

import style from "@agir/front/genericComponents/_variables.scss";

const CardLikeSection = styled.section``;
const StyledColumn = styled(Column)`
  & > ${Card}, & > ${CardLikeSection} {
    @media (max-width: ${style.collapse}px) {
      padding: 1.375rem;
      box-shadow: none;
      border-bottom: 1px solid #c4c4c4;
      margin-bottom: 0;
    }

    &:empty {
      display: none;
    }
  }

  & > ${CardLikeSection} {
    & > h3 {
      margin: 0;
    }
    & > ${Card} {
      padding: 1.375rem 0;
      box-shadow: none;
    }
  }
`;

const IndexLinkAnchor = styled.a`
  font-weight: 600;
  font-size: 12px;
  line-height: 1.4;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  margin: 20px 0 20px -1rem;

  &,
  &:hover,
  &:active {
    text-decoration: none;
    color: #585858;
  }
`;
const IndexLink = () => {
  return (
    <Row>
      <Column grow>
        <IndexLinkAnchor href="#">
          <FeatherIcon name="arrow-left" small />
          &ensp; Liste des événements
        </IndexLinkAnchor>
      </Column>
    </Row>
  );
};

const MobileLayout = (props) => {
  return (
    <Container>
      <Row>
        <StyledColumn stack>
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
            <EventDescription {...props} illustration={null} />
          </Card>
          {props.contact && <ContactCard {...props.contact} />}
          {props.routes.facebook && <EventFacebookLinkCard {...props} />}
          <ShareCard />
          {props.groups.length > 0 && (
            <CardLikeSection>
              <h3>Organisé par</h3>
              {props.groups.map((group, key) => (
                <GroupCard key={key} {...group} />
              ))}
            </CardLikeSection>
          )}
        </StyledColumn>
      </Row>
    </Container>
  );
};

const DesktopLayout = (props) => {
  return (
    <Container>
      <IndexLink />
      <Row gutter={32}>
        <Column grow>
          <div>
            <EventHeader {...props} />
            <EventDescription {...props} />
            {props.groups.length > 0 && (
              <div>
                <h3 style={{ marginBottom: "1rem", marginTop: "2.5rem" }}>
                  Organisé par
                </h3>

                {props.groups.map((group, key) => (
                  <GroupCard key={key} {...group} />
                ))}
              </div>
            )}
          </div>
        </Column>
        <StyledColumn width="380px">
          <EventLocationCard {...props} />
          {props.contact && <ContactCard {...props.contact} />}
          {(props.participantCount > 1 || props.groups.length > 0) && (
            <EventInfoCard {...props} />
          )}
          {props.routes.facebook && <EventFacebookLinkCard {...props} />}
          <ShareCard />
        </StyledColumn>
      </Row>
    </Container>
  );
};

const EventPage = (props) => {
  const { startTime, endTime, ...rest } = props;
  const start =
    typeof startTime === "string"
      ? DateTime.fromISO(startTime).setLocale("fr")
      : typeof startTime === "number"
      ? DateTime.fromMillis(startTime).setLocale("fr")
      : null;
  const end =
    typeof endTime === "string"
      ? DateTime.fromISO(endTime).setLocale("fr")
      : typeof endTime === "number"
      ? DateTime.fromMillis(endTime).setLocale("fr")
      : null;
  const schedule = Interval.fromDateTimes(start, end);
  return (
    <ResponsiveLayout
      {...rest}
      startTime={start}
      endTime={end}
      schedule={schedule}
      DesktopLayout={DesktopLayout}
      MobileLayout={MobileLayout}
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
  startTime: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
    .isRequired,
  endTime: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  location: PropTypes.shape({
    name: PropTypes.string,
    address: PropTypes.string,
    shortAddress: PropTypes.string,
  }),
  participantCount: PropTypes.number.isRequired,
  contact: PropTypes.shape(ContactCard.propTypes),
  options: PropTypes.shape({ price: PropTypes.string }),
  groups: PropTypes.arrayOf(PropTypes.shape(GroupCard.propTypes)),
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

MobileLayout.propTypes = DesktopLayout.propTypes = {
  ...EventPage.propTypes,
  startTime: PropTypes.instanceOf(DateTime),
  endTime: PropTypes.instanceOf(DateTime),
  schedule: PropTypes.instanceOf(Interval),
};

export default EventPage;
