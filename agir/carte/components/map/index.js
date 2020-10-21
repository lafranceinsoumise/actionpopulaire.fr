import "ol/ol.css";
import "./style.css";

export let listMap = async function () {
  const listMapModule = await import("./listMap");

  listMap = listMapModule.default;
  listMap.apply(null, arguments);
};

export let itemMap = async function () {
  const itemMapModule = await import("./itemMap");

  itemMap = itemMapModule.default;
  itemMap.apply(null, arguments);
};
