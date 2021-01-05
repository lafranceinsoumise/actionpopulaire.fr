import { DateTime, Interval } from "luxon";
import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import {
  useDispatch,
  useSelector,
} from "@agir/front/globalContext/GlobalContext";
import { setIs2022 } from "@agir/front/globalContext/actions";
import { getIsConnected } from "@agir/front/globalContext/reducers";

import Link from "@agir/front/app/Link";

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
import Footer from "@agir/front/dashboardComponents/Footer";
import ContactCard from "@agir/front/genericComponents/ContactCard";
import EventInfoCard from "@agir/events/eventPage/EventInfoCard";
import ShareCard from "@agir/front/genericComponents/ShareCard";
import Card from "@agir/front/genericComponents/Card";
import GroupCard from "@agir/groups/groupComponents/GroupCard";

import style from "@agir/front/genericComponents/_variables.scss";
import useSWR from "swr";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";

import logger from "@agir/lib/utils/logger";
const log = logger(__filename);

const CardLikeSection = styled.section``;
const StyledColumn = styled(Column)`
  & > ${Card}, & > ${CardLikeSection} {
    font-size: 14px;
    font-weight: 400;

    & a,
    & strong {
      font-weight: 600;
    }

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

const IndexLinkAnchor = styled(Link)`
  font-weight: 600;
  font-size: 12px;
  line-height: 1.4;
  text-transform: uppercase;
  display: flex;
  align-items: center;
  margin: 20px 0 20px -1rem;

  &,
  &:hover,
  &:focus,
  &:active {
    text-decoration: none;
    color: #585858;
  }

  span {
    transform: rotate(180deg) translateY(-1.5px);
    transform-origin: center center;
  }

  @media (max-width: ${style.collapse}px) {
    padding: 0.5rem 1.375rem 0;
    margin-bottom: -1rem;
  }
`;
const IndexLink = () => (
  <Row>
    <Column grow>
      <IndexLinkAnchor route="events">
        <span>&#10140;</span>
        &ensp; Liste des événements
      </IndexLinkAnchor>
    </Column>
  </Row>
);

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
          {props.logged ? <IndexLink /> : null}
          <Card>
            <EventHeader {...props} />
          </Card>
          <EventLocationCard {...props} />
          <EventInfoCard {...props} />
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
                <GroupCard key={key} {...group} isEmbedded />
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
    <Container style={{ margin: "4rem auto", padding: "0 4rem" }}>
      {props.logged ? <IndexLink /> : null}
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
                  <GroupCard key={key} {...group} isEmbedded />
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

export const EventPage = (props) => {
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
  appRoutes: PropTypes.object,
  logged: PropTypes.bool,
};

MobileLayout.propTypes = DesktopLayout.propTypes = {
  ...EventPage.propTypes,
  startTime: PropTypes.instanceOf(DateTime),
  endTime: PropTypes.instanceOf(DateTime),
  schedule: PropTypes.instanceOf(Interval),
};

const DesktopSkeleton = () => (
  <Container style={{ margin: "4rem auto", padding: "0 4rem" }}>
    <Row gutter={32}>
      <Column grow>
        <Skeleton />
      </Column>
      <Column width="380px">
        <Skeleton />
      </Column>
    </Row>
  </Container>
);

const MobileSkeleton = () => (
  <Container style={{ margin: "2rem auto", padding: "0 1rem" }}>
    <Row>
      <Column>
        <Skeleton />
      </Column>
    </Row>
  </Container>
);

export const ConnectedEventPage = (props) => {
  const { eventPk } = props;
  const isConnected = useSelector(getIsConnected);
  const dispatch = useDispatch();

  const { data: eventData } = useSWR(`/api/evenements/${eventPk}`);
  log.debug("Event data", eventData);

  let { is2022 } = eventData || {};

  React.useEffect(() => {
    is2022 === true && dispatch(setIs2022());
  }, [is2022, dispatch]);

  return (
    <>
      <PageFadeIn
        ready={eventData}
        wait={
          <ResponsiveLayout
            DesktopLayout={DesktopSkeleton}
            MobileLayout={MobileSkeleton}
          />
        }
      >
        {eventData && <EventPage {...eventData} logged={isConnected} />}
      </PageFadeIn>
      <Footer />
    </>
  );
};

ConnectedEventPage.propTypes = {
  eventPk: PropTypes.string,
};

export default ConnectedEventPage;
