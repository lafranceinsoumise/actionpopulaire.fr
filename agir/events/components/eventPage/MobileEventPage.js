import { DateTime, Interval } from "luxon";
import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import defaultEventImage from "@agir/front/genericComponents/images/banner-map-background.svg";

import Card from "@agir/front/genericComponents/Card";
import ClickableMap from "@agir/carte/common/Map/ClickableMap";
import ContactCard from "@agir/front/genericComponents/ContactCard";
import EventDescriptionCard from "./EventDescriptionCard";
import EventFacebookLinkCard from "./EventFacebookLinkCard";
import ReportFormCard from "./ReportFormCard";
import EventHeader from "./EventHeader";
import EventInfoCard from "@agir/events/eventPage/EventInfoCard";
import EventLocationCard from "./EventLocationCard";
import EventPhotosCard from "./EventPhotosCard";
import EventReportCard from "./EventReportCard";
import GroupsCard from "@agir/groups/groupComponents/GroupsCard";
import OnlineUrlCard from "./OnlineUrlCard";
import RenderIfVisible from "@agir/front/genericComponents/RenderIfVisible";
import ShareCard from "@agir/front/genericComponents/ShareCard";

const CardLikeSection = styled.section``;
const StyledMain = styled(RenderIfVisible)`
  a,
  strong {
    font-weight: 600;
  }

  & > ${Card}, & > ${CardLikeSection} {
    font-size: 14px;
    font-weight: 400;
    padding: 1.375rem;
    box-shadow: none;
    border-bottom: 1px solid #c4c4c4;
    margin-bottom: 0;

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

const StyledGroupImage = styled.div``;
const StyledMap = styled(RenderIfVisible)`
  flex: 0 0 424px;
  clip-path: polygon(100% 0%, 100% 100%, 0% 100%, 11% 0%);
  position: relative;
  background-size: 0 0;

  @media (max-width: ${style.collapse}px) {
    clip-path: none;
    width: 100%;
    height: 155px;
    flex-basis: 155px;
    background-size: contain;
    background-position: center center;
    background-repeat: no-repeat;
  }

  & > * {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    height: 100%;
  }

  ${StyledGroupImage} {
    background-position: center center;
    background-repeat: no-repeat;
    background-size: contain;

    &:first-child {
      background-size: cover;
      opacity: 0.2;
    }
  }
`;

const MobileEventPage = (props) => {
  const {
    name,
    contact,
    routes,
    groups,
    groupsAttendees,
    illustration,
    location,
    subtype,
  } = props;

  const hasMap = Array.isArray(location?.coordinates?.coordinates);

  return (
    <>
      <StyledMap
        once
        style={{
          backgroundColor: illustration?.thumbnail
            ? style.white
            : style.secondary500,
          backgroundImage: !illustration?.thumbnail
            ? `url(${defaultEventImage})`
            : undefined,
        }}
      >
        {illustration ? (
          <>
            <StyledGroupImage
              aria-hidden="true"
              style={{ backgroundImage: `url(${illustration?.thumbnail})` }}
            />
            <StyledGroupImage
              aria-hidden="true"
              style={{ backgroundImage: `url(${illustration?.thumbnail})` }}
            />
          </>
        ) : hasMap ? (
          <ClickableMap
            location={location}
            zoom={11}
            iconConfiguration={subtype}
          />
        ) : null}
      </StyledMap>

      <StyledMain once style={{ overflow: "hidden" }}>
        <Card>
          <EventHeader {...props} />
          {props.isOrganizer && <ReportFormCard eventPk={props.id} />}
        </Card>
      </StyledMain>

      <StyledMain once>
        <Card style={{ padding: 0 }}>
          <OnlineUrlCard
            onlineUrl={props.onlineUrl}
            youtubeVideoID={props.youtubeVideoID}
            isPast={props.isPast}
          />
        </Card>
      </StyledMain>

      <StyledMain once>
        <EventLocationCard
          isStatic
          name={name}
          timezone={props.timezone}
          schedule={props.schedule}
          location={location}
          routes={routes}
          subtype={subtype}
          hideMap={illustration === null}
        />
      </StyledMain>

      <StyledMain once>
        <EventInfoCard {...props} />
        <EventPhotosCard {...props} />
        <EventReportCard {...props} />
        <EventDescriptionCard {...props} />
      </StyledMain>

      <StyledMain once>
        {contact && <ContactCard {...contact} />}
        {routes?.facebook && <EventFacebookLinkCard {...props} />}
        <ShareCard url={routes?.details} />
        <GroupsCard title="Organisé par" groups={groups} isDetailed />
        <GroupsCard
          title={`${groupsAttendees.length} groupes participants`}
          groups={groupsAttendees}
        />
      </StyledMain>
    </>
  );
};

MobileEventPage.propTypes = {
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
  startTime: PropTypes.oneOfType([PropTypes.string, PropTypes.number])
    .isRequired,
  endTime: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
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

export default MobileEventPage;
