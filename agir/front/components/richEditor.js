import tinymce from "tinymce/tinymce";
import "tinymce/themes/modern/theme";
import "tinymce/plugins/link";
import "tinymce/plugins/autolink";
import "tinymce/plugins/image";
import "tinymce/plugins/lists";

import "tinymce-i18n/langs/fr_FR";

/**
 * Indique à webpack comment copier les fichiers de skins de tinymce dans
 *
 * Par défaut tinymce inclue les fichiers de skin
 */
require.context(
  "file-loader?name=[path][name].[ext]&outputPath=front&context=node_modules/tinymce!tinymce/skins",
  true,
  /.*/
);

tinymce.init({
  selector: "textarea.richeditorwidget",
  plugins: "link autolink image lists",
  toolbar: "bold italic | formatselect | link image | bullist numlist",
  menubar: false,
  statusbar: false,
  language: "fr_FR",
  block_formats: "Paragraphe=p;Titre=h2;Sous-titre=h3;Petit titre=h4",
});
