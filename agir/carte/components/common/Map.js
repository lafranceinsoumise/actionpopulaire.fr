import * as proj from "ol/proj";
import PropTypes from "prop-types";
import React, { useCallback, useRef, useState } from "react";
import styled, { keyframes } from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import logger from "@agir/lib/utils/logger";

import { fontIsLoaded } from "../map/utils";
import { createMap } from "../map/common";

const log = logger(__filename);

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

  .ol-zoom {
    display: flex;
    flex-flow: column nowrap;
    position: absolute;
    top: 0.25rem;
    left: 0.25rem;
    border: 3px solid #d0e5ec;
    background-color: white;
    border-radius: 3px;
    box-shadow: ${style.elaborateShadow};

    button {
      background-color: #7390bb;
      color: white;
      font-weight: bold;
      font-family: monospace;
      width: 1.5rem;
      height: 1.5rem;
      display: flex;
      align-items: center;
      justify-content: center;
      padding: 0;
      border: none;
      outline: none;
      cursor: pointer;

      &:hover,
      &:focus {
        background-color: #7390bbdd;
      }
    }

    button + button {
      margin-top: 1px;
    }
  }
`;

const Map = (props) => {
  const { center, zoom = 14, iconConfiguration, isStatic, ...rest } = props;

  const [isLoaded, setIsLoaded] = useState(0);
  const mapObject = useRef(null);

  const mapRef = useCallback(
    async (mapElement) => {
      if (mapObject.current && mapElement) {
        mapObject.current.getView().setCenter(proj.fromLonLat(center));
        mapObject.current.getView().setZoom(zoom);
        setIsLoaded(true);
      } else if (mapElement) {
        try {
          await fontIsLoaded("FontAwesome");
          mapObject.current = createMap(
            center,
            zoom,
            mapElement,
            iconConfiguration,
            isStatic
          );
          mapObject.current.once("postrender", () => {
            setIsLoaded(true);
          });
        } catch (e) {
          log.error(e.message);
        }
      }
    },
    [center, zoom, iconConfiguration, isStatic]
  );

  isLoaded && mapObject.current && mapObject.current.updateSize();

  return <StyledMapWrapper ref={mapRef} $isLoaded={isLoaded} {...rest} />;
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
