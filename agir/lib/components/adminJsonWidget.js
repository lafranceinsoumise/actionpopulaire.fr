import JsonEditor from "jsoneditor";

import "jsoneditor/dist/jsoneditor.css";

const loaded = [];

document.addEventListener("DOMContentLoaded", function() {
  document.querySelectorAll(".jsoneditordiv").forEach(e => {
    if (loaded.includes(e.dataset.fieldname)) return;

    const editor = new JsonEditor(e, {
      onChangeText: content => {
        document.getElementById(`id_${e.dataset.fieldname}`).value = content;
      },
      mode: "code"
    });
    editor.set(
      JSON.parse(
        document.getElementById(e.dataset.fieldname + "-data").textContent
      )
    );
    loaded.push(e.dataset.fieldname);
  });
});
