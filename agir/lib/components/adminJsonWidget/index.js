import JsonEditor from "jsoneditor";

import "jsoneditor/dist/jsoneditor.css";
import onDOMReady from "@agir/lib/utils/onDOMReady";

const loaded = [];

const initAdminJsonWidget = () => {
  if (window.AgirAdminJsonWidget) {
    return;
  }

  document.querySelectorAll(".jsoneditordiv").forEach((e) => {
    if (loaded.includes(e.dataset.fieldname)) return;

    const editor = new JsonEditor(e, {
      onChangeText: (content) => {
        document.getElementById(`id_${e.dataset.fieldname}`).value = content;
      },
      templates: [
        {
          text: "Groupe de champs",
          title: "Insérer un groupe de champs",
          value: {
            title: "Mon groupe de champs",
            fields: [],
          },
        },
        {
          text: "Champ",
          title: "Insérer un champ",
          value: {
            id: "identifiant_du_champ",
            label: "Label du champ",
            type: "short_text",
          },
        },
      ],
      modes: ["tree", "code"],
      schema: document.getElementById(e.dataset.fieldname + "-schema")
        ? JSON.parse(
            document.getElementById(e.dataset.fieldname + "-schema").textContent
          )
        : null,
    });
    editor.set(
      JSON.parse(
        document.getElementById(e.dataset.fieldname + "-data").textContent
      )
    );
    editor.expandAll();
    loaded.push(e.dataset.fieldname);
  });

  window.AgirAdminJsonWidget = 1;
};

onDOMReady(initAdminJsonWidget);
