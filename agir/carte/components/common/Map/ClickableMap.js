import React from "react";
import Map from "@agir/carte/common/Map";
import PropTypes from "prop-types";
import styled from "styled-components";
import { useMobileApp } from "@agir/front/app/hooks";

const StyledLink = styled.a`
  position: relative;
  & > * {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    width: 100%;
    height: 100%;
  }
`;

const ClickableMap = (props) => {
  const { location, zoom, iconConfiguration } = props;
  const isIOS = useMobileApp().isIOS;
  const isAndroid = useMobileApp().isAndroid;
  let latitude = location.coordinates.coordinates.toString().split(",")[1];
  let longitude = location.coordinates.coordinates.toString().split(",")[0];

  const appleHref = `https://maps.apple.com/?ll=${latitude},${longitude}&q=${encodeURI(
    location.address,
  )}&ui=maps`;
  const androidHref = `geo:0,0?q=${latitude},${longitude}`;

  let href = `https://www.google.fr/maps/search/${location.address}`;
  if (isAndroid) {
    href = androidHref;
  } else if (isIOS) {
    href = appleHref;
  }

  return (
    <StyledLink href={href} target="_blank" rel="noreferrer">
      <Map
        center={location.coordinates.coordinates}
        staticMapUrl={location.staticMapUrl}
        isStatic={true}
        iconConfiguration={iconConfiguration}
        zoom={zoom}
      />
    </StyledLink>
  );
};

ClickableMap.propTypes = {
  location: PropTypes.shape({
    name: PropTypes.string,
    address: PropTypes.string,
    shortAddress: PropTypes.string,
    coordinates: PropTypes.shape({
      coordinates: PropTypes.arrayOf(PropTypes.number).isRequired,
    }),
    staticMapUrl: PropTypes.string,
  }),
  zoom: PropTypes.number,
  iconConfiguration: PropTypes.shape({
    iconName: PropTypes.string,
    color: PropTypes.string,
    iconUrl: PropTypes.string,
    iconAnchor: PropTypes.string,
  }),
};

export default ClickableMap;
