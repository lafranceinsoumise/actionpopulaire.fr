import { DateTime, Interval } from "luxon";
import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import { DOOR2DOOR_EVENT_SUBTYPE_LABEL } from "@agir/events/common/utils";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getUser } from "@agir/front/globalContext/reducers";

import EventInfoCard from "@agir/events/eventPage/EventInfoCard";
import TokTokCard from "@agir/events/TokTok/TokTokCard";
import BackLink from "@agir/front/app/Navigation/BackLink";
import Card from "@agir/front/genericComponents/Card";
import ContactCard from "@agir/front/genericComponents/ContactCard";
import { Column, Container, Row } from "@agir/front/genericComponents/grid";
import ShareCard from "@agir/front/genericComponents/ShareCard";
import Spacer from "@agir/front/genericComponents/Spacer";
import {
  GroupsJoiningCard,
  GroupsOrganizingCard,
} from "@agir/groups/groupComponents/GroupsCard";
import EventDescriptionCard from "./EventDescriptionCard";
import EventFacebookLinkCard from "./EventFacebookLinkCard";
import EventHeader from "./EventHeader";
import EventLocationCard from "./EventLocationCard";
import EventMessages from "./EventMessages";
import EventPhotosCard from "./EventPhotosCard";
import EventReportCard from "./EventReportCard";
import OnlineUrlCard from "./OnlineUrlCard";
import ReportFormCard from "./ReportFormCard";
import EventSpeakers from "./EventSpeakers";

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

const DesktopEventPage = (props) => {
  const {
    id,
    logged,
    groups,
    contact,
    routes,
    isOrganizer,
    isManager,
    isPast,
    groupsAttendees,
    participantCount,
    subtype,
    backLink,
    eventSpeakers,
  } = props;

  const user = useSelector(getUser);

  // Get groups attendees not organizers, from user only
  const userGroupsAttendees = useMemo(() => {
    if (!Array.isArray(user?.groups)) {
      return [];
    }
    const groupsId = groups?.map((group) => group.id) || [];
    const groupsAttendeesId = groupsAttendees?.map((group) => group.id) || [];
    return user.groups.filter(
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
            <BackLink />
          </Column>
        </Row>
        <Row gutter={32}>
          <Column grow>
            <div>
              <EventHeader {...props} />
              <EventSpeakers
                style={{ margin: "2rem 0" }}
                eventSpeakers={eventSpeakers}
              />
              {isManager && <ReportFormCard eventPk={id} />}
              {logged && subtype.label === DOOR2DOOR_EVENT_SUBTYPE_LABEL && (
                <>
                  <Spacer size="1rem" />
                  <TokTokCard flex />
                </>
              )}
              <OnlineUrlCard
                youtubeVideoID={props.youtubeVideoID}
                onlineUrl={props.onlineUrl}
                isPast={isPast}
              />
              <EventPhotosCard {...props} />
              <EventReportCard {...props} />
              <EventDescriptionCard {...props} />
              <GroupsOrganizingCard
                groups={groups}
                isDetailed
                eventPk={id}
                isPast={isPast}
                isOrganizer={isOrganizer}
                backLink={backLink}
              />
              <GroupsJoiningCard
                eventPk={id}
                isPast={isPast}
                groups={groups}
                groupsAttendees={userGroupsAttendees}
                backLink={backLink}
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
  isManager: PropTypes.bool,
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
  groupsAttendees: PropTypes.array,
  participantCount: PropTypes.number,
  subtype: PropTypes.object,
  backLink: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
  youtubeVideoID: PropTypes.string,
  eventSpeakers: PropTypes.array,
};

export default DesktopEventPage;
