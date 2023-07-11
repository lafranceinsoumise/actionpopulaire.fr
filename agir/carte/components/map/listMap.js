import Feature from "ol/Feature";
import { fromLonLat } from "ol/proj";
import VectorSource from "ol/source/Vector";
import Point from "ol/geom/Point";
import GeoJSON from "ol/format/GeoJSON";
import { Style, Stroke, Fill } from "ol/style";
import VectorLayer from "ol/layer/Vector";

import { fontawesomeIsLoaded, ARROW_SIZE } from "./utils";
import { makeStyle, setUpMap, setUpPopup, fitBounds } from "./common";
import makeLayerControl from "./layerControl";
import makeSearchControl from "./searchControl";
import getFormatPopups from "./itemPopups";

import logger from "@agir/lib/utils/logger";
const log = logger(__filename);

const OFFSET = 0.00005;

function disambiguate(points) {
  const itemMap = Object.create(null);
  let key, n, i, p, angle;

  for (let p of points) {
    key = JSON.stringify(p.coordinates.coordinates);
    itemMap[key] = itemMap[key] || [];
    itemMap[key].push(p);
  }

  for (key of Object.keys(itemMap)) {
    n = itemMap[key].length;
    if (n > 1) {
      for (i = 0; i < n; i++) {
        p = itemMap[key][i];
        angle = Math.PI / 2 + (i * 2 * Math.PI) / n;
        p.coordinates.coordinates = [
          p.coordinates.coordinates[0] + OFFSET * Math.cos(angle),
          p.coordinates.coordinates[1] + OFFSET * Math.sin(angle),
        ];
      }
    }
  }
}

class Display {
  constructor(types, subtypes, listType) {
    this.types = types;
    this.formatPopup = getFormatPopups(listType, types, subtypes);
    this.sources = {};
    this.layers = {};
    this.typeStyles = {};
    this.typePastStyles = {};
    for (let type of types) {
      this.sources[type.id] = new VectorSource();
      this.layers[type.id] = new VectorLayer({ source: this.sources[type.id] });
      this.typeStyles[type.id] = makeStyle(type);
      if (listType === "events") {
        this.typePastStyles[type.id] = makeStyle(type, { color: false });
      }
    }

    // Subtypes
    this.subtypeStyles = {};
    this.subtypePastStyles = {};
    this.popupAnchors = {};
    this.sourceForSubtype = {};
    for (let subtype of subtypes) {
      this.subtypeStyles[subtype.id] =
        makeStyle(subtype) || this.typeStyles[subtype.type];
      if (listType === "events") {
        this.subtypePastStyles[subtype.id] =
          makeStyle(subtype, {
            color: false,
          }) || this.typePastStyles[subtype.type];
      }
      this.popupAnchors[subtype.id] = subtype.popupAnchor;
      this.sourceForSubtype[subtype.id] = this.sources[subtype.type];
    }
  }

  getLayers() {
    return this.types.map((type) => this.layers[type.id]);
  }

  getFeatureFor(item) {
    const feature = new Feature({
      geometry: new Point(fromLonLat(item.coordinates.coordinates)),
      popupAnchor: (this.popupAnchors[item.subtype] || -5) - ARROW_SIZE,
      popupContent: this.formatPopup(item),
    });
    feature.setId(item.id);

    if (item.subtype && this.subtypeStyles[item.subtype]) {
      if (
        typeof item.end_time === "undefined" ||
        new Date(item.end_time) > new Date()
      ) {
        feature.setStyle(this.subtypeStyles[item.subtype]);
      } else {
        feature.setStyle(this.subtypePastStyles[item.subtype]);
      }
    } else {
      feature.setStyle(this.typeStyles[item.type]);
    }

    return feature;
  }

  updateFeatures(data, hideInactive) {
    for (let item of data) {
      const feature = this.getFeatureFor(item);
      const source = item.subtype
        ? this.sourceForSubtype[item.subtype]
        : this.sources[item.type];
      if (!source) {
        continue;
      }
      if (hideInactive && !item.is_active && item.location_country === "FR") {
        source.hasFeature(feature) &&
          source.removeFeature(source.getFeatureById(item.id));
        continue;
      }
      if (!source.hasFeature(feature)) {
        source.addFeature(feature);
      }
    }
  }

  getControls(data) {
    return makeLayerControl(
      this.types.map((type) => ({
        label: type.label,
        color: type.color,
        layer: this.layers[type.id],
      })),
      (hideInactive) => this.updateFeatures(data, hideInactive),
    );
  }
}

export default async function listMap(
  htmlElementId,
  {
    endpoint,
    listType,
    types,
    subtypes,
    bounds,
    focusGeometry,
    showSearch = true,
    showActiveControl = true,
    showLayerControl = true,
  },
) {
  const display = new Display(types, subtypes, listType);

  var geometryLayers = [];
  if (focusGeometry) {
    const geom = new GeoJSON().readGeometry(focusGeometry);

    if (!bounds) {
      bounds = geom.getExtent().slice(); // need to duplicate because this array is mutated by OpenLayers
    }

    const feature = new Feature(geom.transform("EPSG:4326", "EPSG:3857")); // project from LatLon to Mercator
    feature.setStyle(
      new Style({
        stroke: new Stroke({
          color: "red",
          width: 1,
        }),
        fill: new Fill({
          color: "rgba(255,234,28,0.1)",
        }),
      }),
    );
    const source = new VectorSource();
    source.addFeature(feature);
    const layer = new VectorLayer({ source });
    geometryLayers.push(layer);
  }

  bounds = bounds || [-5.3, 41.2, 9.6, 51.2]; // default bounds are metropolitan France

  const map = setUpMap(
    htmlElementId,
    geometryLayers.concat(display.getLayers()),
  );
  fitBounds(map, bounds);
  setUpPopup(map);

  let data;
  try {
    const res = await fetch(endpoint, {
      method: "GET",
      credentials: "include",
      mode: "no-cors",
    });
    if (res.status !== 200) {
      return;
    }
    data = await res.json();
  } catch (e) {
    return;
  }

  try {
    await fontawesomeIsLoaded();
  } catch (e) {
    log.debug("Error loading fonts."); // eslint-disable-line no-console
  }

  disambiguate(data);
  display.updateFeatures(data, showActiveControl && listType === "groups");

  // Controls
  const [hideInactiveButton, layerControlButton, layerControl] =
    display.getControls(data);

  if (showLayerControl && types.length > 1) {
    layerControlButton.setMap(map);
    layerControl.setMap(map);
  }

  if (showActiveControl && listType === "groups") {
    map.addControl(hideInactiveButton);
  }

  if (showSearch) {
    const geosearchControl = makeSearchControl(map.getView());
    map.addControl(geosearchControl);
  }
}
