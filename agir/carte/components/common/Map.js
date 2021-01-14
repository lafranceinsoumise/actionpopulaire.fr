import * as proj from "ol/proj";
import PropTypes from "prop-types";
import React, { useEffect, useRef, useState } from "react";
import styled, { keyframes } from "styled-components";

import { createMap } from "../map/common";

import "../map/style.css";

const skeleton = keyframes`
  to {
    background-position: 350% 0, 0 0;
  }
`;

const StyledMapWrapper = styled.div`
  width: 100%;
  height: 100%;
  background-color: lightgrey;
  background-image: linear-gradient(
      100deg,
      rgba(230, 230, 230, 0) 0,
      rgba(230, 230, 230, 1) 50%,
      rgba(230, 230, 230, 0) 100%
    ),
    linear-gradient(rgba(220, 220, 220, 1) 100%, transparent 0%);
  background-size: 33% 100%, 100% 100%;
  background-position: -150% 0, 0 0;
  background-repeat: no-repeat;
  animation: ${skeleton} 2.5s infinite ease-in;
  animation-play-state: ${({ $isLoaded }) =>
    $isLoaded ? "paused" : "running"};

  & > * {
    opacity: ${({ $isLoaded }) => ($isLoaded ? "1" : 0)};
    transition: opacity 500ms ease-in-out;
  }
`;

const Map = (props) => {
  const { center, zoom = 14, iconConfiguration, isStatic, ...rest } = props;

  const [isLoaded, setIsLoaded] = useState(0);
  const mapElement = useRef();
  const map = useRef(null);

  useEffect(() => {
    if (map.current && mapElement.current) {
      map.current.getView().setCenter(proj.fromLonLat(center));
      map.current.getView().setZoom(zoom);
    } else if (mapElement.current) {
      map.current = createMap(
        center,
        zoom,
        mapElement.current,
        iconConfiguration,
        isStatic
      );
      map.current.once("postrender", () => {
        setIsLoaded(true);
      });
    }
  }, [center, zoom, iconConfiguration, isStatic]);

  return <StyledMapWrapper ref={mapElement} $isLoaded={isLoaded} {...rest} />;
};
Map.propTypes = {
  isStatic: PropTypes.bool,
  center: PropTypes.arrayOf(PropTypes.number).isRequired,
  zoom: PropTypes.number,
  iconConfiguration: PropTypes.shape({
    iconName: PropTypes.string,
    color: PropTypes.string,
    iconUrl: PropTypes.string,
    iconAnchor: PropTypes.string,
  }),
};
export default Map;
