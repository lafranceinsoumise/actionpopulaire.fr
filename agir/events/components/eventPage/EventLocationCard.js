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

import ClickableMap from "@agir/carte/common/Map/ClickableMap";
import AddToCalendarWidget from "./AddToCalendarWidget";

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
  border-bottom: 1px solid ${style.black50};
`;

const EventLocationCard = (props) => {
  const {
    name,
    schedule,
    location,
    routes,
    subtype,
    isStatic,
    hideMap,
    timezone,
  } = props;
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
          {localInterval ? (
            <IconListItem name="clock">
              <strong>({schedule.start.zoneName})</strong>
              <br />
              {interval}
              <span
                style={{
                  paddingTop: 4,
                  display: "block",
                  color: style.black500,
                }}
              >
                <strong>({timezone})</strong>
                <br />
                {localInterval}
              </span>
            </IconListItem>
          ) : (
            <IconListItem name="clock">{interval}</IconListItem>
          )}
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
          <Column grow>
            <AddToCalendarWidget routes={routes} name={name} />
          </Column>
        </Row>
      </div>
    </StyledCard>
  );
};
EventLocationCard.propTypes = {
  name: PropTypes.string,
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
