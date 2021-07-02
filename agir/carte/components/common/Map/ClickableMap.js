import React from "react";
import Map from "@agir/carte/common/Map";
import PropTypes from "prop-types";
import { useMobileApp } from "@agir/front/app/hooks";

const ClickableMap = (props) => {
  const { location, zoom, iconConfiguration } = props;
  const isIOS = useMobileApp().isIOS;
  const isAndroid = useMobileApp().isAndroid;
  let latitude = location.coordinates.coordinates.toString().split(",")[1];
  let longitude = location.coordinates.coordinates.toString().split(",")[0];

  const appleHref = `https://maps.apple.com/?ll=${latitude},${longitude}&ui=maps`;
  const androidHref = `geo:${latitude},${longitude}`;

  let href = `https://www.google.fr/maps/search/${location.address}`;
  if (isAndroid) {
    href = androidHref;
  } else if (isIOS) {
    href = appleHref;
  }

  return (
    <Map
      as={"a"}
      href={href}
      target="_blank"
      center={location.coordinates.coordinates}
      staticMapUrl={location.staticMapUrl}
      isStatic={true}
      iconConfiguration={iconConfiguration}
      zoom={zoom}
    />
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
