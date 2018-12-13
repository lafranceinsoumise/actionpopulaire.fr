import Feature from "ol/Feature";
import * as proj from "ol/proj";
import VectorSource from "ol/source/Vector";
import axios from "axios/index";
import Point from "ol/geom/Point";
import VectorLayer from "ol/layer/Vector";

import { fontIsLoaded, ARROW_SIZE } from "./utils";
import { makeStyle, setUpMap, setUpPopup, fitBounds } from "./common";
import makeLayerControl from "./layerControl";
import makeSearchControl from "./searchControl";

const OFFSET = 0.00005;
function disambiguate(points) {
  const map = Object.create(null);
  let key, n, i, p, angle;

  for (let p of points) {
    key = JSON.stringify(p.coordinates.coordinates);
    map[key] = map[key] || [];
    map[key].push(p);
  }

  for (key of Object.keys(map)) {
    n = map[key].length;
    if (n > 1) {
      for (i = 0; i < n; i++) {
        p = map[key][i];
        angle = Math.PI / 2 + (i * 2 * Math.PI) / n;
        p.coordinates.coordinates = [
          p.coordinates.coordinates[0] + OFFSET * Math.cos(angle),
          p.coordinates.coordinates[1] + OFFSET * Math.sin(angle)
        ];
      }
    }
  }
}

export default async function listMap(
  htmlElementId,
  { endpoint, type, types, subtypes, formatPopup, bounds }
) {
  bounds = bounds || [-5.3, 41.2, 9.6, 51.2];

  // Type filters
  const sources = {},
    layers = {},
    typeStyles = {};
  for (let type of types) {
    sources[type.id] = new VectorSource();
    layers[type.id] = new VectorLayer({ source: sources[type.id] });
    typeStyles[type.id] = makeStyle(type);
  }

  const map = setUpMap(htmlElementId, types.map(type => layers[type.id]));
  fitBounds(map, bounds);
  setUpPopup(map);

  // Subtypes
  const subtypeStyles = {},
    popupAnchors = {},
    sourceForSubtype = {};
  for (let subtype of subtypes) {
    subtypeStyles[subtype.id] = makeStyle(subtype) || typeStyles[subtype.type];
    popupAnchors[subtype.id] = subtype.popupAnchor;
    sourceForSubtype[subtype.id] = sources[subtype.type];
  }

  // Drawing function
  var draw = function(data, hideInactive) {
    for (let item of data) {
      const feature = new Feature({
        geometry: new Point(proj.fromLonLat(item.coordinates.coordinates)),
        popupAnchor: (popupAnchors[item.subtype] || -5) - ARROW_SIZE,
        popupContent: formatPopup(item)
      });
      feature.setId(item.id);

      if (item.subtype && subtypeStyles[item.subtype]) {
        feature.setStyle(subtypeStyles[item.subtype]);
        if (hideInactive && item.current_events_count === 0) {
          if (sourceForSubtype[item.subtype].hasFeature(feature)) {
            sourceForSubtype[item.subtype].removeFeature(
              sourceForSubtype[item.subtype].getFeatureById(item.id)
            );
          }
        } else if (!sourceForSubtype[item.subtype].hasFeature(feature)) {
          sourceForSubtype[item.subtype].addFeature(feature);
        }
      } else {
        feature.setStyle(typeStyles[item.type]);
        if (hideInactive && item.current_events_count === 0) {
          if (sources[item.type].hasFeature(feature)) {
            sources[item.type].removeFeature(
              sources[item.type].getFeatureById(item.id)
            );
          }
        } else if (!sources[item.type].hasFeature(feature)) {
          sources[item.type].addFeature(feature);
        }
      }
    }
  };

  // Data request
  const res = await axios.get(endpoint);
  if (res.status !== 200) {
    return;
  }

  try {
    await fontIsLoaded("FontAwesome");
  } catch (e) {
    console.log("Error loading fonts."); // eslint-disable-line no-console
  }

  disambiguate(res.data);
  draw(res.data, type === "groups");

  // Controls
  const [
    hideInactiveButton,
    layerControlButton,
    layerControl
  ] = makeLayerControl(
    types.map(type => ({
      label: type.label,
      color: type.color,
      layer: layers[type.id]
    })),
    hideInactive => draw(res.data, hideInactive)
  );

  if (types.length > 1) {
    layerControlButton.setMap(map);
    layerControl.setMap(map);
  }

  if (type === "groups") {
    map.addControl(hideInactiveButton);
  }

  const geosearchControl = makeSearchControl(map.getView());
  map.addControl(geosearchControl);
}
