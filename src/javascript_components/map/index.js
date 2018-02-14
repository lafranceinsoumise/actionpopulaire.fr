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
  const popupElement = document.createElement('div');
  popupElement.className = 'map_popup';
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
    const features = map.getFeaturesAtPixel(evt.pixel);
    if (features) {
      const coords = features[0].getGeometry().getCoordinates();
      popup.getElement().innerHTML = features[0].get('popupContent');
      popup.setOffset([0, features[0].get('popupAnchor')]);
      popup.setPosition(coords);
    }
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
        text: new Text({
          text: fontawesome(style.iconName),
          font: 'normal 18px FontAwesome',
          fill: new Fill({
            color: style.color
          })
        })
      }),
      new Style({
        image: new Circle({
          radius: 12,
          fill: new Fill({
            color: 'white'
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
  const element = document.createElement('div');
  element.className = 'layer_selector';
  layersConfig.forEach(function (layerConfig) {
    const label = document.createElement('label');
    const input = document.createElement('input');
    input.type = 'checkbox';
    input.checked = true;
    const span = document.createElement('span');
    span.textContent = layerConfig.label;
    span.style.color = layerConfig.color;
    label.appendChild(input);
    label.appendChild(span);

    input.addEventListener('change', function () {
      layerConfig.layer.setVisible(input.checked);
    });

    element.appendChild(label);
  });

  return new Control({
    element,
  });
}

function makeSearchControl(view) {
  const provider = new OpenStreetMapProvider();
  const element = document.createElement('div');
  element.className = 'search_box';
  element.innerHTML = `
  <form><input type="text" id="search"><button type="submit"><i class="fa fa-search"></i></button></form>
  <ul class="results"></ul>
  `;

  const form = element.getElementsByTagName('form')[0];
  const input = element.querySelector('#search');
  const list = element.getElementsByTagName('ul')[0];

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

  form.addEventListener('submit', function (e) {
    e.preventDefault();
    provider.search({query: input.value}).then(function (results) {
      if (results.length) {
        list.innerHTML = results.slice(0, 3).map(r => (
          `<li><a href="#" data-cx="${r.x}" data-cy="${r.y}">${r.label}</a></li>`
        )).join('');
      } else {
        list.innerHTML = '<li><em>Pas de résultats</em></li>';
      }
      list.classList.add('show');
    });
  });

  element.addEventListener('click', function (ev) {
    ev.stopPropagation();
  });
  document.addEventListener('click', function () {
    list.classList.remove('show')
  });

  return new Control({
    element,
  });
}

export function listMap(htmlElementId, endpoint, types, subtypes, formatPopup) {
  const sources = {}, layers = {}, typeStyles = {};
  for (let type of types) {
    sources[type.id] = new VectorSource();
    layers[type.id] = new VectorLayer({source: sources[type.id]});
    typeStyles[type.id] = makeStyle(type);
  }

  const layerControl = makeLayerControl(types.map(type => ({label: type.label, color: type.color, layer: layers[type.id]})));

  const map = setUpMap(htmlElementId, types.map(type => layers[type.id]));
  fitFrance(map);
  setUpPopup(map);
  layerControl.setMap(map);

  const geosearchControl = makeSearchControl(map.getView());
  map.addControl(geosearchControl);

  const subtypeStyles = {}, popupAnchors = {}, sourceForSubtype = {};
  for (let subtype of subtypes) {
    subtypeStyles[subtype.id] = makeStyle(subtype) || typeStyles[subtype.type];
    popupAnchors[subtype.id] = subtype.popupAnchor;
    sourceForSubtype[subtype.id] = sources[subtype.type];
  }

  axios.get(endpoint).then(function (res) {
    if (res.status !== 200) {
      return;
    }

    for (let item of res.data) {
      const feature = new Feature({
        geometry: new Point(proj.fromLonLat(item.coordinates.coordinates)),
        popupAnchor: popupAnchors[item.subtype] - ARROW_SIZE,
        popupContent: formatPopup(item),
      });

      if (item.subtype) {
        feature.setStyle(subtypeStyles[item.subtype]);
        sourceForSubtype[item.subtype].addFeature(feature);
      } else {
        feature.setStyle(typeStyles[item.type]);
        sources[item.type].addFeature(feature);
      }
    }
  });
}

export function itemMap(htmlElementId, coordinates, iconConfiguration) {
  const style = makeStyle(iconConfiguration);
  const feature = new Feature({
    geometry: new Point(proj.fromLonLat(coordinates))
  });
  feature.setStyle(style);
  const layer = new VectorLayer({
    source: new VectorSource({features: [feature]})
  });
  const map = setUpMap(htmlElementId, [layer]);
  map.getView().setCenter(proj.fromLonLat(coordinates));
  map.getView().setZoom(14);
}
