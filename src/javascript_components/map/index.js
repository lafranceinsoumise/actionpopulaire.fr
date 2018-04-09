import Map from 'ol/map';
import View from 'ol/view';
import Feature from 'ol/feature';
import Point from 'ol/geom/point';
import TileLayer from 'ol/layer/tile';
import VectorSource from 'ol/source/vector';
import VectorLayer from 'ol/layer/vector';
import OSM from 'ol/source/osm';
import Style from 'ol/style/style';
import Text from 'ol/style/text';
import Circle from 'ol/style/circle';
import Fill from 'ol/style/fill';
import Icon from 'ol/style/icon';
import Overlay from 'ol/overlay';
import Control from 'ol/control/control';
import proj from 'ol/proj';
import axios from 'axios';
import {OpenStreetMapProvider} from 'leaflet-geosearch';
import fontawesome from 'fontawesome';

import {element, fontIsLoaded} from './utils';

import 'ol/ol.css';
import './style.css';

const ARROW_SIZE = 20;

function setUpMap(elementId, layers) {
  const view = new View({
    center: proj.fromLonLat([2, 47]),
    zoom: 6
  });
  return new Map({
    target: elementId,
    layers: [
      new TileLayer({
        source: new OSM()
      }),
      ...layers
    ],
    view
  });
}

function fitFrance(map) {
  map.getView().fit(
    proj.transformExtent([-5.3, 41.2, 9.6, 51.2], 'EPSG:4326', 'EPSG:3857'), map.getSize()
  );
}

function setUpPopup(map) {
  const popupElement = element('div', [], {
    'className': 'map_popup'
  });
  popupElement.addEventListener('mousedown', function (evt) {
    evt.stopPropagation();
  });

  const popup = new Overlay({
    element: popupElement,
    positioning: 'bottom-center',
    offset: [0, -ARROW_SIZE],
    stopEvent: false,
  });

  map.addOverlay(popup);

  map.on('singleclick', function (evt) {
    popup.setPosition();
    map.forEachFeatureAtPixel(evt.pixel, function (feature) {
      const coords = feature.getGeometry().getCoordinates();
      popup.getElement().innerHTML = feature.get('popupContent');
      popup.setOffset([0, feature.get('popupAnchor')]);
      popup.setPosition(coords);
      return true;
    });
  });

  map.on('pointermove', function (evt) {
    const hit = this.forEachFeatureAtPixel(evt.pixel, function () {
      return true;
    });
    if (hit) {
      this.getTargetElement().style.cursor = 'pointer';
    } else {
      this.getTargetElement().style.cursor = '';
    }
  });
}

function makeStyle(style) {
  if (style.color && style.iconName) {
    return [
      new Style({
        image: new Circle({
          radius: 12,
          fill: new Fill({
            color: 'white'
          })
        })
      }),
      new Style({
        text: new Text({
          text: fontawesome(style.iconName),
          font: 'normal 18px FontAwesome',
          fill: new Fill({
            color: style.color
          })
        })
      })
    ];
  }
  else if (style.iconUrl && style.iconAnchor) {
    return new Style({
      image: new Icon({
        anchor: style.iconAnchor,
        anchorXUnits: 'pixels',
        anchorYUnits: 'pixels',
        opacity: 1,
        src: style.iconUrl
      })
    });
  }

  return null;
}

function makeLayerControl(layersConfig) {
  const selectors = layersConfig.map(function (layerConfig) {
    const input = element('input', [], {type: 'checkbox', checked: true});
    const label = element('label', [
      input,
      ['span', [layerConfig.label], {style: {color: layerConfig.color}}]
    ]);

    input.addEventListener('change', function () {
      layerConfig.layer.setVisible(input.checked);
    });

    return label;
  });

  const layerButton = element('button', [fontawesome('bars')]);
  const layerButtonContainer = element(
    'div', [layerButton],
    {className: 'ol-unselectable ol-control layer_selector_button'}
  );

  const layerBox = element('div', selectors, {className: 'layer_selector'});

  layerButton.addEventListener('click', function() {
    layerButton.textContent = layerBox.classList.toggle('visible') ? fontawesome('times') : fontawesome('bars');
  });

  return [
    new Control({element: layerButtonContainer}),
    new Control({element: layerBox})
  ];
}

function makeSearchControl(view) {
  const provider = new OpenStreetMapProvider();

  const input = element('input', [], {type: 'text'});
  const list = element('ul', [], {className: 'results'});
  const form = element('form', [
    input,
    ['button', [
      ['i', [], {className: 'fa fa-search'}]
    ]]
  ]);

  const control = element('div', [form, list], {className: 'search_box'});

  list.addEventListener('click', function (e) {
    e.preventDefault();
    if (e.target.tagName === 'A') {
      view.animate({
        center: proj.fromLonLat([+e.target.dataset.cx, +e.target.dataset.cy]),
        zoom: 14
      });
      list.classList.remove('show');
    }
  });

  form.addEventListener('submit', async function (e) {
    e.preventDefault();
    try {
      const results = await provider.search({query: input.value});
      if (results.length) {
        list.innerHTML = results.slice(0, 3).map(r => (
          `<li><a href="#" data-cx="${r.x}" data-cy="${r.y}">${r.label}</a></li>`
        )).join('');
      } else {
        list.innerHTML = '<li><em>Pas de résultats</em></li>';
      }
      list.classList.add('show');
    } catch (e) {
      list.innerHTML = '<li><em>Impossible de contacter le service de recherche d\'adresses</em></li>';
      list.classList.add('show');
    }
  });

  control.addEventListener('click', function (ev) {
    ev.stopPropagation();
  });
  document.addEventListener('click', function () {
    list.classList.remove('show');
  });

  return new Control({
    element: control,
  });
}


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
        console.log('disambiguate: ', p.name)
        angle = Math.PI / 2 + i * 2 * Math.PI / n;
        p.coordinates.coordinates = [
          p.coordinates.coordinates[0] + OFFSET * Math.cos(angle),
          p.coordinates.coordinates[1] + OFFSET * Math.sin(angle)
        ];
      }
    }
  }
}


export async function listMap(htmlElementId, endpoint, types, subtypes, formatPopup) {
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

export async function itemMap(htmlElementId, coordinates, iconConfiguration) {
  const style = makeStyle(iconConfiguration);
  const feature = new Feature({
    geometry: new Point(proj.fromLonLat(coordinates))
  });
  feature.setStyle(style);
  const layer = new VectorLayer({
    source: new VectorSource({features: [feature]})
  });
  await fontIsLoaded('FontAwesome');
  const map = setUpMap(htmlElementId, [layer]);
  map.getView().setCenter(proj.fromLonLat(coordinates));
  map.getView().setZoom(14);
}
