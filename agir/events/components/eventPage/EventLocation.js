import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import FeatherIcon, {
  IconList,
  IconListItem,
} from "@agir/front/genericComponents/FeatherIcon";
import Card from "@agir/front/genericComponents/Card";

import style from "@agir/front/genericComponents/style.scss";
import googleLogo from "./assets/Google.svg";
import outlookLogo from "./assets/Outlook.svg";
import { Column, Row } from "@agir/front/genericComponents/grid";

const dateFormat = {
  weekday: "long",
  month: "long",
  day: "numeric",
  hour: "numeric",
  minute: "2-digit",
};

const EventLocationCard = styled(Card)`
  font-weight: 500;
`;

const LocationName = styled.span`
  color: ${style.brandBlack};
`;

const WithLinebreak = styled.span`
  white-space: pre-line;
  color: ${style.gray};
`;

const MapContainer = styled.div`
  border-radius: 0.5rem 0.5rem 0 0;
  margin: -1.5rem -1.5rem 0.5rem;
`;

const MapIframe = styled.iframe.attrs((props) => ({
  src: props.src,
  ...props,
}))`
  display: block;
  border: 0;
  border-radius: 0.5rem 0.5rem 0 0;

  width: 100%;
  min-height: 300px;
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
    border-left: 1px ${style.grayLight} solid;
    padding-left: 1rem;
  }
`;

const EventLocation = ({ date, location, routes }) => {
  return (
    <EventLocationCard>
      <MapContainer>
        <MapIframe src={routes.map} />
      </MapContainer>
      <IconList>
        <IconListItem name="clock">
          {date.toLocaleString(dateFormat)}
        </IconListItem>
        <IconListItem name="map-pin">
          <WithLinebreak>
            <LocationName>{location.name}</LocationName>
            {"\n"}
            {location.address}
          </WithLinebreak>
        </IconListItem>
      </IconList>
      <Row>
        <Column fill width={["content", "content"]}>
          <a href={routes.exportCalendar}>Ajouter à mon agenda</a>
        </Column>
        <Column width={["content", "content"]}>
          <CalendarButtonHolder>
            <li>
              <a href={routes.googleCalendar}>
                <img src={googleLogo} alt="logo Google" />
              </a>
            </li>
            <li>
              <a href={routes.outlookCalendar}>
                <img src={outlookLogo} alt="logo Outlook" />
              </a>
            </li>
          </CalendarButtonHolder>
        </Column>
      </Row>
    </EventLocationCard>
  );
};
EventLocation.propTypes = {
  date: PropTypes.string,
  location: PropTypes.shape({
    name: PropTypes.string,
    address: PropTypes.string,
  }),
  routes: PropTypes.shape({
    map: PropTypes.string,
    googleCalendar: PropTypes.string,
    outlookCalendar: PropTypes.string,
    exportCalendar: PropTypes.string,
  }),
};

export default EventLocation;
