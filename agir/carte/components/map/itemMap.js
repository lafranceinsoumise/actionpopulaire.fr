/* eslint-env browser */

import Feature from "ol/Feature";
import { fromLonLat } from "ol/proj";
import VectorSource from "ol/source/Vector";
import Point from "ol/geom/Point";
import VectorLayer from "ol/layer/Vector";

import { fontawesomeIsLoaded } from "./utils";
import { makeStyle, setUpMap } from "./common";

import logger from "@agir/lib/utils/logger";
const log = logger(__filename);

export default async function itemMap(
  htmlElementId,
  coordinates,
  iconConfiguration,
) {
  const style = makeStyle(iconConfiguration);
  const feature = new Feature({
    geometry: new Point(fromLonLat(coordinates)),
  });
  feature.setStyle(style);
  const layer = new VectorLayer({
    source: new VectorSource({ features: [feature] }),
  });

  try {
    await fontawesomeIsLoaded();
  } catch (e) {
    log.debug("Error loading fonts."); // eslint-disable-line no-console
  }

  const map = setUpMap(htmlElementId, [layer]);
  map.getView().setCenter(fromLonLat(coordinates));
  map.getView().setZoom(14);
}
