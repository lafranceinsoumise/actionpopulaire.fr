import "core-js/stable";
import "regenerator-runtime/runtime";

export default function onDOMReady(listener) {
  document.addEventListener("turbolinks:load", listener);
  if (document.readyState !== "loading") {
    listener();
  }
}
