import Control from "ol/control/Control";
import * as proj from "ol/proj";
import { OpenStreetMapProvider } from "leaflet-geosearch";

import { element } from "./utils";

export default function makeSearchControl(view) {
  const provider = new OpenStreetMapProvider();

  const input = element("input", [], { type: "text" });
  const list = element("ul", [], { className: "results" });
  const form = element("form", [
    input,
    ["button", [["i", [], { className: "fa fa-search" }]]]
  ]);

  const control = element("div", [form, list], { className: "search_box" });

  list.addEventListener("click", function(e) {
    e.preventDefault();
    if (e.target.tagName === "A") {
      view.animate({
        center: proj.fromLonLat([+e.target.dataset.cx, +e.target.dataset.cy]),
        zoom: 14
      });
      list.classList.remove("show");
    }
  });

  form.addEventListener("submit", async function(e) {
    e.preventDefault();
    try {
      const results = await provider.search({ query: input.value });
      if (results.length) {
        list.innerHTML = results
          .slice(0, 3)
          .map(
            r =>
              `<li><a href="#" data-cx="${r.x}" data-cy="${r.y}">${r.label}</a></li>`
          )
          .join("");
      } else {
        list.innerHTML = "<li><em>Pas de résultats</em></li>";
      }
      list.classList.add("show");
    } catch (e) {
      list.innerHTML =
        "<li><em>Impossible de contacter le service de recherche d'adresses</em></li>";
      list.classList.add("show");
    }
  });

  control.addEventListener("click", function(ev) {
    ev.stopPropagation();
  });
  document.addEventListener("click", function() {
    list.classList.remove("show");
  });

  return new Control({
    element: control
  });
}
