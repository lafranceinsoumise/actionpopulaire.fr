import { DateTime, Interval } from "luxon";
import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import Card from "@agir/front/genericComponents/Card";
import { Column, Container, Row } from "@agir/front/genericComponents/grid";
import ContactCard from "@agir/front/genericComponents/ContactCard";
import EventDescriptionCard from "./EventDescriptionCard";
import EventFacebookLinkCard from "./EventFacebookLinkCard";
import ReportFormCard from "./ReportFormCard";
import EventHeader from "./EventHeader";
import EventMessages from "./EventMessages";
import EventInfoCard from "@agir/events/eventPage/EventInfoCard";
import EventLocationCard from "./EventLocationCard";
import EventPhotosCard from "./EventPhotosCard";
import EventReportCard from "./EventReportCard";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import {
  GroupsOrganizingCard,
  GroupsJoiningCard,
} from "@agir/groups/groupComponents/GroupsCard";
import Link from "@agir/front/app/Link";
import OnlineUrlCard from "./OnlineUrlCard";
import ShareCard from "@agir/front/genericComponents/ShareCard";
import Spacer from "@agir/front/genericComponents/Spacer";
import TokTokCard from "@agir/events/TokTok/TokTokCard";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";

import { DOOR2DOOR_EVENT_SUBTYPE_LABEL } from "@agir/events/common/utils";

const CardLikeSection = styled.section``;
const StyledColumn = styled(Column)`
  a,
  strong {
    font-weight: 600;
  }

  & > ${Card}, & > ${CardLikeSection} {
    font-size: 14px;
    font-weight: 400;

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
  margin: 2.5rem 1rem 1.5rem;

  &,
  &:hover,
  &:focus,
  &:active {
    text-decoration: none;
    color: #585858;
  }

  svg {
    height: 16px;
  }
`;

const DesktopEventPage = (props) => {
  const {
    id,
    logged,
    groups,
    groupsAttendees,
    contact,
    participantCount,
    routes,
    subtype,
    isOrganizer,
    isPast,
  } = props;

  const user = useSelector(getUser);

  // Get groups attendees not organizers, from user only
  const userGroupsAttendees = useMemo(() => {
    const groupsId = groups?.map((group) => group.id) || [];
    const groupsAttendeesId = groupsAttendees?.map((group) => group.id) || [];
    return user?.groups.filter(
      (group) =>
        groupsAttendeesId.includes(group.id) && !groupsId.includes(group.id)
    );
  }, [user, groups, groupsAttendees]);

  return (
    <>
      <Container
        style={{
          margin: "0 auto 4rem",
          padding: "0 4rem",
          maxWidth: "1336px",
          width: "100%",
        }}
      >
        <Row style={{ minHeight: 56 }}>
          <Column grow>
            {logged && (
              <IndexLinkAnchor route="events">
                <FeatherIcon name="arrow-left" /> &nbsp; Liste des événements
              </IndexLinkAnchor>
            )}
          </Column>
        </Row>
        <Row gutter={32}>
          <Column grow>
            <div>
              <EventHeader {...props} />
              {isOrganizer && <ReportFormCard eventPk={id} />}
              {logged && subtype.label === DOOR2DOOR_EVENT_SUBTYPE_LABEL && (
                <TokTokCard flex />
              )}
              <OnlineUrlCard
                youtubeVideoID={props.youtubeVideoID}
                onlineUrl={props.onlineUrl}
                isPast={isPast}
              />
              <EventPhotosCard {...props} />
              <EventReportCard {...props} />
              <EventDescriptionCard {...props} />

              {Array.isArray(groups) && groups.length > 0 && (
                <>
                  <GroupsOrganizingCard
                    groups={groups}
                    isDetailed
                    eventPk={id}
                    isPast={isPast}
                    isOrganizer={isOrganizer}
                  />
                  <Spacer size="1rem" />
                </>
              )}
              <GroupsJoiningCard
                eventPk={id}
                isPast={isPast}
                groups={groups}
                groupsAttendees={userGroupsAttendees}
              />

              <EventMessages eventPk={props.id} />
            </div>
          </Column>
          <StyledColumn width="380px">
            <EventLocationCard {...props} />
            {contact && <ContactCard {...contact} />}
            {(participantCount > 1 || groups?.length > 0 || subtype?.label) && (
              <EventInfoCard {...props} />
            )}
            {routes?.facebook && <EventFacebookLinkCard {...props} />}
            <ShareCard url={routes?.details} />
          </StyledColumn>
        </Row>
      </Container>
    </>
  );
};

DesktopEventPage.propTypes = {
  id: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  hasSubscriptionForm: PropTypes.bool,
  isOrganizer: PropTypes.bool,
  rsvp: PropTypes.string,
  compteRendu: PropTypes.string,
  compteRenduPhotos: PropTypes.arrayOf(PropTypes.object),
  illustration: PropTypes.shape({
    thumbnail: PropTypes.string,
  }),
  description: PropTypes.string,
  location: PropTypes.shape({
    name: PropTypes.string,
    address: PropTypes.string,
    shortAddress: PropTypes.string,
    coordinates: PropTypes.shape({
      coordinates: PropTypes.arrayOf(PropTypes.number),
    }),
    staticMapUrl: PropTypes.string,
  }),
  contact: PropTypes.shape(ContactCard.propTypes),
  options: PropTypes.shape({ price: PropTypes.string }),
  groups: PropTypes.array,
  routes: PropTypes.shape({
    page: PropTypes.string,
    map: PropTypes.string,
    join: PropTypes.string,
    cancel: PropTypes.string,
    manage: PropTypes.string,
    manageMobile: PropTypes.string,
    calendarExport: PropTypes.string,
    googleExport: PropTypes.string,
    facebook: PropTypes.string,
    addPhoto: PropTypes.string,
    compteRendu: PropTypes.string,
  }),
  appRoutes: PropTypes.object,
  logged: PropTypes.bool,
  onlineUrl: PropTypes.string,
  startTime: PropTypes.instanceOf(DateTime),
  endTime: PropTypes.instanceOf(DateTime),
  schedule: PropTypes.instanceOf(Interval),
  isPast: PropTypes.bool,
};

export default DesktopEventPage;
