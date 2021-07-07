import tinymce from "tinymce/tinymce";

// Thème et icônes
import "tinymce/themes/silver";
import "tinymce/icons/default";

// Localisation française
import "tinymce-i18n/langs/fr_FR";

// Plugins
import "tinymce/plugins/link";
import "tinymce/plugins/autolink";
import "tinymce/plugins/image";
import "tinymce/plugins/lists";
import onDOMReady from "@agir/lib/utils/onDOMReady";

/**
 * Indique à webpack comment copier les fichiers de skins de tinymce dans
 *
 * Par défaut tinymce inclue les fichiers de skin
 */
require.context(
  "file-loader?name=[path][name].[ext]&context=node_modules/tinymce!tinymce/skins",
  true,
  /.*/
);

const config = {
  selector: "textarea.richeditorwidget",
  plugins: "link autolink image lists",
  toolbar: "bold italic | formatselect | link image | bullist numlist",
  menubar: false,
  statusbar: false,
  language: "fr_FR",
  block_formats: "Paragraphe=p;Titre=h2;Sous-titre=h3;Petit titre=h4",
  skin: "oxide",
  skin_url: "/static/components/skins/ui/oxide",
};

const initRichEditor = () => {
  if (!window.AgirRichEditor) {
    tinymce.init(config);
    window.AgirRichEditor = 1;
  }
};

onDOMReady(initRichEditor);
