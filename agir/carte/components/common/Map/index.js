import React, { Suspense } from "react";
import PropTypes from "prop-types";
import { lazy } from "@agir/front/app/utils";

import StaticMap from "./StaticMap";
const OpenLayersMap = lazy(() => import("./OpenLayersMap.js"));

const Map = (props) =>
  props.isStatic && props.staticMapUrl ? (
    <StaticMap {...props} />
  ) : (
    <Suspense fallback={null}>
      <OpenLayersMap {...props} />
    </Suspense>
  );

Map.propTypes = {
  isStatic: PropTypes.bool, // hide controls
  staticMapUrl: PropTypes.string,
  center: PropTypes.arrayOf(PropTypes.number),
  zoom: PropTypes.number,
};

export default Map;
