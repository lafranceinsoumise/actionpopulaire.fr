import Map from "ol/Map";
import View from "ol/View";
import TileLayer from "ol/layer/Tile";
import OSM from "ol/source/OSM";
import Style from "ol/style/Style";
import Text from "ol/style/Text";
import Circle from "ol/style/Circle";
import Fill from "ol/style/Fill";
import Icon from "ol/style/Icon";
import Overlay from "ol/Overlay";
import * as proj from "ol/proj";
import fontawesome from "fontawesome";

import { element } from "./utils";

const ARROW_SIZE = 20;

export function setUpMap(elementId, layers) {
  const view = new View({
    center: proj.fromLonLat([2, 47]),
    zoom: 6,
  });
  return new Map({
    target: elementId,
    layers: [
      new TileLayer({
        source: new OSM(),
      }),
      ...layers,
    ],
    view,
  });
}

export function fitBounds(map, bounds) {
  map
    .getView()
    .fit(proj.transformExtent(bounds, "EPSG:4326", "EPSG:3857"), map.getSize());
}

export function setUpPopup(map) {
  const popupElement = element("div", [], {
    className: "map_popup",
  });
  popupElement.addEventListener("mousedown", function (evt) {
    evt.stopPropagation();
  });

  const popup = new Overlay({
    element: popupElement,
    positioning: "bottom-center",
    offset: [0, -ARROW_SIZE],
    stopEvent: true,
  });

  map.addOverlay(popup);

  map.on("singleclick", function (evt) {
    popup.setPosition();
    map.forEachFeatureAtPixel(evt.pixel, function (feature) {
      const coords = feature.getGeometry().getCoordinates();
      if (feature.get("popupContent")) {
        popup.getElement().innerHTML = feature.get("popupContent");
        popup.setOffset([0, feature.get("popupAnchor")]);
        popup.setPosition(coords);
        return true;
      }
    });
  });

  map.on("pointermove", function (evt) {
    const hit = this.forEachFeatureAtPixel(evt.pixel, function (feature) {
      return !!feature.get("popupContent");
    });
    if (hit) {
      this.getTargetElement().style.cursor = "pointer";
    } else {
      this.getTargetElement().style.cursor = "";
    }
  });
}

export function makeStyle(style, options = {}) {
  options = Object.assign({ color: true }, options);

  if (style.color && style.iconName) {
    return [
      new Style({
        image: new Circle({
          radius: 12,
          fill: new Fill({
            color: "white",
          }),
        }),
      }),
      new Style({
        text: new Text({
          text: fontawesome(style.iconName),
          font: "normal 18px FontAwesome",
          fill: new Fill({
            color: options.color ? style.color : "#999",
          }),
        }),
      }),
    ];
  } else if (style.iconUrl && style.iconAnchor) {
    return new Style({
      image: new Icon({
        anchor: style.iconAnchor,
        anchorXUnits: "pixels",
        anchorYUnits: "pixels",
        opacity: 1,
        src: style.iconUrl,
      }),
    });
  }

  return null;
}
