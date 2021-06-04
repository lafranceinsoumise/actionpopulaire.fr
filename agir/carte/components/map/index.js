import "ol/ol.css";
import "./style.css";

export async function listMap() {
  const listMapModule = (await import("./listMap")).default;

  listMapModule.apply(null, arguments);
}

export async function itemMap() {
  const itemMapModule = (await import("./itemMap")).default;

  itemMapModule.apply(null, arguments);
}
