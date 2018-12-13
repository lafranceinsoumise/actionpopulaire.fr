/* eslint-env browser, jquery */

import Masonry from "masonry-layout";

const elem = document.querySelector(".masonry");
new Masonry(elem, {
  itemSelector: ".col-md-6",
  percentPosition: true
});

$('[data-toggle="tooltip"]').tooltip();
