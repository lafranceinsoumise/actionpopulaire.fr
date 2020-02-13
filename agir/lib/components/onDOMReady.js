import "core-js/stable";
import "regenerator-runtime/runtime";

export default function onDOMReady(listener) {
  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", listener);
  } else {
    listener();
  }
  document.addEventListener("turbolinks:load", listener);
}
