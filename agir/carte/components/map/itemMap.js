import Feature from 'ol/feature';
import proj from 'ol/proj';
import VectorSource from 'ol/source/vector';
import Point from 'ol/geom/point';
import VectorLayer from 'ol/layer/vector';

import {fontIsLoaded} from './utils';
import {makeStyle, setUpMap} from './common';

export default async function itemMap(htmlElementId, coordinates, iconConfiguration) {
  const style = makeStyle(iconConfiguration);
  const feature = new Feature({
    geometry: new Point(proj.fromLonLat(coordinates))
  });
  feature.setStyle(style);
  const layer = new VectorLayer({
    source: new VectorSource({features: [feature]})
  });

  try {
    await fontIsLoaded('FontAwesome');
  } catch (e) {
    console.log('Error loading fonts.');
  }

  const map = setUpMap(htmlElementId, [layer]);
  map.getView().setCenter(proj.fromLonLat(coordinates));
  map.getView().setZoom(14);
}
