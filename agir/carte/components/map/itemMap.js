/* eslint-env browser */

import Feature from "ol/Feature";
import * as proj from "ol/proj";
import VectorSource from "ol/source/Vector";
import Point from "ol/geom/Point";
import VectorLayer from "ol/layer/Vector";

import { fontIsLoaded } from "./utils";
import { makeStyle, setUpMap } from "./common";

import logger from "@agir/lib/utils/log";
const log = logger(__filename);

export default async function itemMap(
  htmlElementId,
  coordinates,
  iconConfiguration
) {
  const style = makeStyle(iconConfiguration);
  const feature = new Feature({
    geometry: new Point(proj.fromLonLat(coordinates)),
  });
  feature.setStyle(style);
  const layer = new VectorLayer({
    source: new VectorSource({ features: [feature] }),
  });

  try {
    await fontIsLoaded("FontAwesome");
  } catch (e) {
    log.debug("Error loading fonts."); // eslint-disable-line no-console
  }

  const map = setUpMap(htmlElementId, [layer]);
  map.getView().setCenter(proj.fromLonLat(coordinates));
  map.getView().setZoom(14);
}
