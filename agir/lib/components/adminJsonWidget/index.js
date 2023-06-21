import JsonEditor from "jsoneditor";

import "jsoneditor/dist/jsoneditor.css";

import onDOMReady from "@agir/lib/utils/onDOMReady";

const DEFAULT_TEMPLATES = [
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
];

const loaded = [];

const initAdminJsonWidget = () => {
  if (window.AgirAdminJsonWidget) {
    return;
  }

  document.querySelectorAll(".jsoneditordiv").forEach((e) => {
    if (loaded.includes(e.dataset.fieldname)) return;

    let schema;
    let templates;
    let data = "";

    e.closest(".form-row").style.overflow = "visible";

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

    if (document.getElementById(e.dataset.fieldname + "-templates")) {
      try {
        templates = document.getElementById(
          e.dataset.fieldname + "-templates"
        ).textContent;
        templates = JSON.parse(templates);
      } catch (e) {
        console.log(e);
        templates = undefined;
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
      language: "fr-FR",
      onChangeText: (content) => {
        document.getElementById(`id_${e.dataset.fieldname}`).value = content;
      },
      templates: templates || DEFAULT_TEMPLATES,
      mode: typeof data === "string" ? "code" : "tree",
      modes: ["tree", "code", "preview"],
      schema: schema,
      schemaRefs: {},
      allowSchemaSuggestions: true,
    });

    typeof data === "string" ? editor.setText(data) : editor.set(data);
    editor.expandAll && editor.expandAll();
    loaded.push(e.dataset.fieldname);

    window.AgirAdminJsonWidgetEditor = editor;
  });

  window.AgirAdminJsonWidget = 1;
};

onDOMReady(initAdminJsonWidget);
