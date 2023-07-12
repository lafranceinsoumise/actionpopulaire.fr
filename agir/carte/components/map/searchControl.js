import Control from "ol/control/Control";
import { fromLonLat } from "ol/proj";
import { OpenStreetMapProvider } from "leaflet-geosearch";
import {
  from,
  fromEvent,
  merge,
  debounceTime,
  map,
  filter,
  switchMap,
  startWith,
  tap,
} from "rxjs";

import { element } from "./utils";

export default function makeSearchControl(view) {
  const provider = new OpenStreetMapProvider();

  const input = element("input", [], { type: "text" });
  const list = element("ul", [], { className: "results" });
  const form = element("form", [
    input,
    ["button", [["i", [], { className: "fa fa-search" }]]],
  ]);

  const control = element("div", [form, list], { className: "search_box" });

  async function search(value) {
    let results;
    try {
      results = await provider.search({ query: value });
    } catch (e) {
      return {
        error: "Impossible de contacter le service de recherche d'adresses.",
      };
    }
    if (results.length === 0) {
      return { error: "Lieu inconnu" };
    }
    return { results: results };
  }

  function goToCoordinates(coords) {
    view.animate({
      center: fromLonLat(coords),
      zoom: 14,
    });
  }

  function updateResults(results) {
    list.innerHTML = results
      .map(
        (r) =>
          `<li><a href="#" data-cx="${r.x}" data-cy="${r.y}">${r.label}</a></li>`,
      )
      .join("");
    list.classList.add("show");
  }

  function displayError(error) {
    list.innerHTML = `<li><em>${error}</em></li>`;
    list.classList.add("show");
  }

  function hideList() {
    list.classList.remove("show");
  }

  control.addEventListener("click", function (ev) {
    ev.stopPropagation();
  });

  const documentClicked$ = fromEvent(document, "click");
  const debouncedInputChange$ = fromEvent(input, "input").pipe(
    debounceTime(700),
    filter((e) => e.target.value.length > 3),
  );
  const formSubmitted$ = fromEvent(form, "submit").pipe(
    tap((e) => e.preventDefault()),
  );
  const listLinkClicked$ = fromEvent(list, "click").pipe(
    filter((e) => e.target.tagName === "A"),
    tap((e) => e.preventDefault()),
    map((e) => [+e.target.dataset.cx, +e.target.dataset.cy]),
  );

  // l'observable des requêtes réalisées à partir du champ de recherche
  // Une requête est lancée soit après un input debouncé, soit après
  // validation du formulaire.
  const results$ = merge(
    formSubmitted$,
    formSubmitted$.pipe(
      startWith(null),
      switchMap(() => debouncedInputChange$), // permet "d'annuler" le debounce si on valide le formulaire
    ),
  ).pipe(
    map(() => input.value), // la valeur du champ
    switchMap((v) => from(search(v))), // le switchMap permet d'éviter d'afficher une requête précédente en cours
  );

  // faire un switchMap depuis documentClicked$ permet d'annuler la recherche
  // en cas de clic en dehors de la boîte en cours de debounce ou de requête
  documentClicked$
    .pipe(
      startWith(null),
      switchMap(() => results$),
    )
    .subscribe(({ error, results }) =>
      error ? displayError(error) : updateResults(results),
    );

  listLinkClicked$.subscribe({
    next: (coords) => {
      goToCoordinates(coords);
      hideList();
    },
  });

  documentClicked$.subscribe({ next: hideList });

  return new Control({
    element: control,
  });
}
