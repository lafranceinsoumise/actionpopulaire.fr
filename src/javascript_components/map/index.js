import L from 'leaflet';
import {GeoSearchControl, OpenStreetMapProvider} from 'leaflet-geosearch';
import axios from 'axios';

import 'leaflet/dist/leaflet.css';
import 'leaflet-geosearch/assets/css/leaflet.css';

import {getQueryParameterByName} from './utils';


function getOptions() {
  return {
    mode: getQueryParameterByName('mode'),
    noCluster: getQueryParameterByName('no_cluster'),
    borderfit: (getQueryParameterByName('borderfit') || '41.783787,9.587328,51.352263,-4.627801').split(','),
    embedEventType: getQueryParameterByName('event_type') || 'groups,evenements_locaux,national,partielles',
    embedTags: getQueryParameterByName('tags') ? getQueryParameterByName('tags').split(',') : [],
    embedEventId: getQueryParameterByName('event_id') || '',
    zipcode: getQueryParameterByName('zipcode'),
    embedCirconscription: getQueryParameterByName('circonscriptions'),
    hidePanel: getQueryParameterByName('hide_panel'),
    hideAddress: getQueryParameterByName('hide_address'),
    geolocation: getQueryParameterByName('geolocation')
  };
}

function makeIcon(type) {
  return L.icon({
    iconUrl: type.iconUrl,
    iconAnchor: type.iconAnchor,
    popupAnchor: type.popupAnchor
  });
}

function makeLayer(type) {
  return L.layerGroup();
}

function addAddressSearch(map) {
  const provider = new OpenStreetMapProvider();
  const searchControl = new GeoSearchControl({
    provider,
    showMarker: false,
    searchLabel: 'Rechercher une adresse'
  });
  searchControl.addTo(map);
}

// Function definitions
function zoomZipcode(map, zipcode) {
  axios.get('//nominatim.openstreetmap.org/search/?format=json&q=' + zipcode + ',France').then(function (res) {
    if (res.status !== 200) {
      throw new Error('Impossible de contacter le service de localisation');
    }
    const data = res.data;

    if (data.length === 0) return;

    zoomCoordinates(map, data[0].lon, data[0].lat);
  });
}


function zoomGeolocation(map) {
  if (!('geolocation' in window.navigator)) {
    return;
  }
  window.navigator.geolocation.getCurrentPosition(function (position) {
    zoomCoordinates(map, position.coords.longitude, position.coords.latitude);
  }, function () {
  }, {
    maximumAge: 0,
    timeout: 5000,
    enableHighAccuracy: true
  });
}

function zoomCoordinates(map, lon, lat) {
  map.setView([lat, lon], 12);
}

function setUpMap(elementId) {
  const tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    attribution: '<a href="http://osm.org/copyright">OpenStreetMap</a>'
  });
  const latlng = L.latLng(43, 2);
  return L.map(elementId, {
    center: latlng,
    zoom: 6,
    layers: [tiles],
    zoomSnap: 0
  });
}

export function listMap(htmlElementId, endpoint, types, subtypes, formatPopup) {
  const options = getOptions();

  const map = setUpMap(htmlElementId);

  map.fitBounds([
    [41.783787,9.587328],
    [51.352263,-4.627801]
  ]);

  // Create all the icon types from the subtypes
  const icons = {};
  subtypes.forEach(function (subtype) {
    icons[subtype.id] = makeIcon(subtype);
  });

  // create all the layers from the types
  const iconLayers = {};
  types.forEach(function (type) {
    iconLayers[type.id] = makeLayer(type, options.noCluster);
    iconLayers[type.id].addTo(map);
  });

  // Controls
  if (!options.hidePanel || options.hidePanel !== 1) {
    let overlayMaps = {};

    for (let type of types) {
      const label = `${type.label}`;
      overlayMaps[label] = iconLayers[type.id];
    }

    L.control.layers(null, overlayMaps, {
      collapsed: false
    }).addTo(map);
  }

  // Show address search
  if (!options.hideAddress || options.hixdeAddress !== 1) {
    addAddressSearch(map);
  }

  /**
   * Step 2. Zoom and event requests
   */
  if (options.geolocation) {
    zoomGeolocation();
  }
  else if (options.zipcode) {
    zoomZipcode(options.zipcode);
  }

  axios.get(endpoint).then(function(res) {
    if(res.status !== 200) {
      return;
    }

    for(let item of res.data) {
      const marker = L.marker([item.coordinates.coordinates[1], item.coordinates.coordinates[0]], {
        icon: icons[item.subtype]
      });
      marker.bindPopup(formatPopup(item));
      iconLayers[subtypes.find(subtype => subtype.id === item.subtype).type].addLayer(marker);
    }
  });
}

export function itemMap(htmlElementId, coordinates, iconConfiguration, popupContent) {
  const map = setUpMap(htmlElementId);

  const icon = makeIcon(iconConfiguration);

  const latLng = L.latLng(coordinates[1], coordinates[0]);
  const marker = L.marker(latLng, {icon});
  marker.bindPopup(popupContent);
  marker.addTo(map);
  map.setView(latLng, 14);
}
