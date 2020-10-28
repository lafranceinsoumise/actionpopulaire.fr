export default function onDOMReady(listener) {
  document.addEventListener("DOMContentLoaded", listener);
  if (document.readyState !== "loading") {
    listener();
  }
}
