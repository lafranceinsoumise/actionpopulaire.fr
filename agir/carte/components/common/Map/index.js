import React from "react";
import PropTypes from "prop-types";

import InteractiveMap from "./Map";
import StaticMap from "./StaticMap";

const Map = (props) =>
  props.isStatic && props.staticMapUrl ? (
    <StaticMap {...props} />
  ) : (
    <InteractiveMap {...props} />
  );

Map.propTypes = {
  isStatic: PropTypes.bool,
  staticMapUrl: PropTypes.string,
};

export default Map;
