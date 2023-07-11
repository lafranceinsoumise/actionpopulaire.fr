import "ol/ol.css";
import "@agir/carte/map/style.css";
import listMap from "@agir/carte/map/listMap";

var types = JSON.parse(document.getElementById("typesConfig").textContent);
var subtypes = JSON.parse(
  document.getElementById("subtypesConfig").textContent,
);
var bounds = JSON.parse(document.getElementById("boundsConfig").textContent);
var queryParams = JSON.parse(
  document.getElementById("queryParams").textContent,
);

var commune = null;
var communeScriptElement = document.getElementById("communeScript");
if (communeScriptElement) {
  commune = JSON.parse(communeScriptElement.textContent);
}

listMap("map", {
  endpoint: "/carte/liste_groupes/" + queryParams,
  listType: "groups",
  types,
  subtypes,
  bounds,
  focusGeometry: commune,
});
