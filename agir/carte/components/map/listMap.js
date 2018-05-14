import Feature from 'ol/feature';
import proj from 'ol/proj';
import VectorSource from 'ol/source/vector';
import axios from 'axios/index';
import Point from 'ol/geom/point';
import VectorLayer from 'ol/layer/vector';

import {fontIsLoaded, ARROW_SIZE} from './utils';
import {makeStyle, setUpMap, setUpPopup, fitFrance} from './common';
import makeLayerControl from './layerControl';
import makeSearchControl from './searchControl';

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
        angle = Math.PI / 2 + i * 2 * Math.PI / n;
        p.coordinates.coordinates = [
          p.coordinates.coordinates[0] + OFFSET * Math.cos(angle),
          p.coordinates.coordinates[1] + OFFSET * Math.sin(angle)
        ];
      }
    }
  }
}

export default async function listMap(htmlElementId, endpoint, types, subtypes, formatPopup) {
  const sources = {}, layers = {}, typeStyles = {};
  for (let type of types) {
    sources[type.id] = new VectorSource();
    layers[type.id] = new VectorLayer({source: sources[type.id]});
    typeStyles[type.id] = makeStyle(type);
  }

  const map = setUpMap(htmlElementId, types.map(type => layers[type.id]));
  fitFrance(map);
  setUpPopup(map);

  if (types.length > 1) {
    const [layerControlButton, layerControl] = makeLayerControl(types.map(type => ({
      label: type.label,
      color: type.color,
      layer: layers[type.id]
    })));
    layerControlButton.setMap(map);
    layerControl.setMap(map);
  }

  const geosearchControl = makeSearchControl(map.getView());
  map.addControl(geosearchControl);

  const subtypeStyles = {}, popupAnchors = {}, sourceForSubtype = {};
  for (let subtype of subtypes) {
    subtypeStyles[subtype.id] = makeStyle(subtype) || typeStyles[subtype.type];
    popupAnchors[subtype.id] = subtype.popupAnchor;
    sourceForSubtype[subtype.id] = sources[subtype.type];
  }

  const res = await axios.get(endpoint);
  if (res.status !== 200) {
    return;
  }

  await fontIsLoaded('FontAwesome');

  disambiguate(res.data);
  for (let item of res.data) {
    const feature = new Feature({
      geometry: new Point(proj.fromLonLat(item.coordinates.coordinates)),
      popupAnchor: (popupAnchors[item.subtype] || -5) - ARROW_SIZE,
      popupContent: formatPopup(item),
    });

    if (item.subtype && subtypeStyles[item.subtype]) {
      feature.setStyle(subtypeStyles[item.subtype]);
      sourceForSubtype[item.subtype].addFeature(feature);
    } else {
      feature.setStyle(typeStyles[item.type]);
      sources[item.type].addFeature(feature);
    }
  }
}
