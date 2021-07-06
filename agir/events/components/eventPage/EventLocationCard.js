import { Interval } from "luxon";
import React, { useMemo } from "react";
import PropTypes from "prop-types";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Card from "@agir/front/genericComponents/Card";
import { Column, Row } from "@agir/front/genericComponents/grid";
import {
  IconList,
  IconListItem,
} from "@agir/front/genericComponents/FeatherIcon";
import Map from "@agir/carte/common/Map";

import { dateFromISOString, displayInterval } from "@agir/lib/utils/time";

import googleLogo from "./assets/Google.svg";
import outlookLogo from "./assets/Outlook.svg";
import ClickableMap from "@agir/carte/common/Map/ClickableMap";

const LocationName = styled.span`
  color: ${style.black1000};
`;

const WithLinebreak = styled.span`
  white-space: pre-line;
  color: ${style.black500};
`;

const MapContainer = styled.div`
  margin: -1.5rem -1.5rem 1.5rem;

  @media (max-width: ${style.collapse}px) {
    margin: 24px 0 0 0;

    * {
      border-radius: ${style.borderRadius};
    }
  }

  & > * {
    display: block;
    border: 0;
    width: 100%;
    min-height: 216px;
  }
`;

const StyledCard = styled(Card)`
  @media (max-width: ${style.collapse}px) {
    display: flex;
    flex-flow: column-reverse;
  }
  margin-bottom: 24px;
  overflow: hidden;
  border-bottom: 1px solid ${style.black50};
`;

const CalendarButtonHolder = styled.ul`
  margin: 0;
  padding: 0;

  li {
    display: inline;
    list-style: none;
  }

  * + * {
    margin-left: 1rem;
    border-left: 1px ${style.black100} solid;
    padding-left: 1rem;
  }
`;

const EventLocationCard = ({
  schedule,
  location,
  routes,
  subtype,
  isStatic,
  hideMap,
  timezone,
}) => {
  const { interval, localInterval } = useMemo(() => {
    let interval = displayInterval(schedule);
    interval = interval.charAt(0).toUpperCase() + interval.slice(1);

    let localInterval = null;
    if (schedule.start.zoneName !== timezone) {
      localInterval = Interval.fromDateTimes(
        dateFromISOString(schedule.start.toISO(), timezone),
        dateFromISOString(schedule.end.toISO(), timezone)
      );
      localInterval = displayInterval(localInterval);
      localInterval =
        localInterval.charAt(0).toUpperCase() + localInterval.slice(1);
      localInterval = localInterval !== interval ? localInterval : null;
    }
    return { interval, localInterval };
  }, [schedule, timezone]);

  return (
    <StyledCard>
      {location && location.coordinates && !hideMap ? (
        <MapContainer>
          {location?.coordinates?.coordinates ? (
            <>
              {isStatic ? (
                <ClickableMap
                  location={location}
                  zoom={14}
                  iconConfiguration={subtype}
                />
              ) : (
                <Map
                  zoom={14}
                  center={location.coordinates.coordinates}
                  iconConfiguration={subtype}
                  isStatic={isStatic}
                />
              )}
            </>
          ) : (
            <iframe src={routes.map} />
          )}
        </MapContainer>
      ) : null}
      <div>
        <IconList>
          <IconListItem name="clock">
            {interval}
            {localInterval && (
              <span style={{ display: "block", color: "#999999" }}>
                {localInterval} ({timezone})
              </span>
            )}
          </IconListItem>
          {location && (location.name || location.address) && (
            <IconListItem name="map-pin">
              <WithLinebreak>
                {location.name && (
                  <>
                    <LocationName>{location.name}</LocationName>
                    {"\n"}
                  </>
                )}
                {location.address}
              </WithLinebreak>
            </IconListItem>
          )}
        </IconList>
        <Row style={{ marginTop: "0.5rem" }}>
          <Column grow width={["content", "content"]}>
            <a href={routes.calendarExport}>Ajouter à mon agenda</a>
          </Column>
          <Column width={["content", "content"]}>
            <CalendarButtonHolder>
              <li>
                <a href={routes.googleExport}>
                  <img
                    src={googleLogo}
                    width="16"
                    height="16"
                    alt="logo Google"
                  />
                </a>
              </li>
              <li>
                <a href={routes.calendarExport}>
                  <img
                    src={outlookLogo}
                    width="16"
                    height="16"
                    alt="logo Outlook"
                  />
                </a>
              </li>
            </CalendarButtonHolder>
          </Column>
        </Row>
      </div>
    </StyledCard>
  );
};
EventLocationCard.propTypes = {
  timezone: PropTypes.string,
  schedule: PropTypes.instanceOf(Interval),
  location: PropTypes.shape({
    name: PropTypes.string,
    address: PropTypes.string,
    coordinates: PropTypes.object,
  }),
  routes: PropTypes.shape({
    map: PropTypes.string,
    calendarExport: PropTypes.string,
    googleExport: PropTypes.string,
  }),
  subtype: PropTypes.object,
  isStatic: PropTypes.bool,
  hideMap: PropTypes.bool,
};

export default EventLocationCard;
