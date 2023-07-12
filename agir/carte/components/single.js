import "ol/ol.css";
import "@agir/carte/map/style.css";
import itemMap from "@agir/carte/map/itemMap";

var subtype = JSON.parse(document.getElementById("subtypeConfig").textContent);
var coordinates = JSON.parse(
  document.getElementById("coordinates").textContent,
);

itemMap("map", coordinates, subtype);
