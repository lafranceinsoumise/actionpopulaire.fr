/* eslint-env browser, jquery */

import Masonry from "masonry-layout";

const elem = document.querySelector(".masonry");
new Masonry(elem, {
  itemSelector: ".gblock",
  percentPosition: true,
});

const blocks = document.querySelectorAll(".gblock");
for (let i = 0; i < blocks.length; i++) {
  blocks[i].style.float = "none";
}

$('[data-toggle="tooltip"]').tooltip();
