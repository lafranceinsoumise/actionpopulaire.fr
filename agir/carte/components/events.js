import "ol/ol.css";
import "@agir/carte/map/style.css";
import listMap from "@agir/carte/map/listMap";

var types = JSON.parse(document.getElementById("typeConfig").textContent);
var subtypes = JSON.parse(document.getElementById("subtypeConfig").textContent);
var bounds = JSON.parse(document.getElementById("boundsConfig").textContent);
var controls = JSON.parse(document.getElementById("controls").textContent);
var queryParams = JSON.parse(
  document.getElementById("queryParams").textContent,
);

var commune = null;
var communeScriptElement = document.getElementById("communeScript");
if (communeScriptElement) {
  commune = JSON.parse(communeScriptElement.textContent);
}

listMap("map", {
  endpoint: "/carte/liste_evenements/" + queryParams,
  listType: "events",
  types,
  subtypes,
  bounds,
  focusGeometry: commune,
  showSearch: controls.search,
  showActiveControl: controls.active,
  showLayerControl: controls.layers,
});
