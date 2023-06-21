import JsonEditor from "jsoneditor";

import "jsoneditor/dist/jsoneditor.css";
import onDOMReady from "@agir/lib/utils/onDOMReady";

const loaded = [];

const initAdminJsonWidget = () => {
  if (window.AgirAdminJsonWidget) {
    return;
  }

  document.querySelectorAll(".jsoneditordiv").forEach((e) => {
    console.log("Boom");

    if (loaded.includes(e.dataset.fieldname)) return;

    let schema = "";
    let data = "";

    if (document.getElementById(e.dataset.fieldname + "-schema")) {
      try {
        schema = document.getElementById(
          e.dataset.fieldname + "-schema"
        ).textContent;
        schema = JSON.parse(schema);
      } catch (e) {
        console.log(e);
        schema = undefined;
      }
    }

    if (document.getElementById(e.dataset.fieldname + "-data").textContent) {
      try {
        data = document.getElementById(
          e.dataset.fieldname + "-data"
        ).textContent;
        data = JSON.parse(data);
      } catch (e) {
        console.log(e);
      }
    }

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
      mode: typeof data === "string" ? "code" : "tree",
      modes: ["tree", "code", "preview"],
      schema: schema,
    });

    typeof data === "string" ? editor.setText(data) : editor.set(data);
    typeof data !== "string" && editor.expandAll();
    loaded.push(e.dataset.fieldname);

    window.AgirAdminJsonWidgetEditor = editor;
  });

  window.AgirAdminJsonWidget = 1;
};

onDOMReady(initAdminJsonWidget);
