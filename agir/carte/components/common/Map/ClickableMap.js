import React from "react";
import Map from "@agir/carte/common/Map";
import PropTypes from "prop-types";

const ClickableMap = (props) => {
  const { location, zoom, subtype, center } = props;
  let latitude = location.coordinates.coordinates.toString().split(",")[1];
  let longitude = location.coordinates.coordinates.toString().split(",")[0];
  return (
    <Map
      as={"a"}
      // android : center={location.coordinates.coordinates}
      href={`https://www.google.fr/maps/search/${location.address}`}
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
};

export default ClickableMap;
