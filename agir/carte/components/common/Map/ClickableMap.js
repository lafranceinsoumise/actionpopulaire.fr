import React from "react";
import Map from "@agir/carte/common/Map";
import PropTypes from "prop-types";
import {useMobileApp} from "@agir/front/app/hooks";

const ClickableMap = (props) => {
  const { location, zoom, subtype, center } = props;
  const isIOS = useMobileApp().isIOS;
  const isAndroid = useMobileApp().isAndroid;
  let latitude = location.coordinates.coordinates.toString().split(",")[1];
  let longitude = location.coordinates.coordinates.toString().split(",")[0];

  const appleHref = `https://maps.apple.com/?ll=${latitude},${longitude}`;
  const androidHref = `geo:${latitude},${longitude}?q=${location.address}`;

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
      center={center}
      isStatic={true}
      iconConfiguration={subtype}
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
      coordinates: PropTypes.arrayOf(PropTypes.number),
    }),
    staticMapUrl: PropTypes.string,
  }),
  center: PropTypes.arrayOf(PropTypes.number).isRequired,
  zoom: PropTypes.number,
  iconConfiguration: PropTypes.shape({
    iconName: PropTypes.string,
    color: PropTypes.string,
    iconUrl: PropTypes.string,
    iconAnchor: PropTypes.string,
  }),
};

export default ClickableMap;
