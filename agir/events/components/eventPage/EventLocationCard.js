import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import {
  IconList,
  IconListItem,
} from "@agir/front/genericComponents/FeatherIcon";
import Card from "@agir/front/genericComponents/Card";
import { Interval } from "luxon";

import style from "@agir/front/genericComponents/_variables.scss";
import googleLogo from "./assets/Google.svg";
import outlookLogo from "./assets/Outlook.svg";
import { Column, Hide, Row } from "@agir/front/genericComponents/grid";
import { displayInterval } from "@agir/lib/utils/time";

const LocationName = styled.span`
  color: ${style.black1000};
`;

const WithLinebreak = styled.span`
  white-space: pre-line;
  color: ${style.black500};
`;

const MapContainer = styled.div`
  margin: -1.5rem -1.5rem 1.5rem;
`;

const MapIframe = styled.iframe.attrs((props) => ({
  src: props.src,
  ...props,
}))`
  display: block;
  border: 0;

  width: 100%;
  min-height: 216px;
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

const EventLocationCard = ({ schedule, location, routes }) => {
  let interval = displayInterval(schedule);
  interval = interval.charAt(0).toUpperCase() + interval.slice(1);
  return (
    <Card>
      {location && location.coordinates && (
        <Hide under>
          <MapContainer>
            <MapIframe src={routes.map} />
          </MapContainer>
        </Hide>
      )}
      <IconList>
        <IconListItem name="clock">{interval}</IconListItem>
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
                <img src={googleLogo} alt="logo Google" />
              </a>
            </li>
            <li>
              <a href={routes.calendarExport}>
                <img src={outlookLogo} alt="logo Outlook" />
              </a>
            </li>
          </CalendarButtonHolder>
        </Column>
      </Row>
    </Card>
  );
};
EventLocationCard.propTypes = {
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
};

export default EventLocationCard;
