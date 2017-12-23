import tinymce from 'tinymce/tinymce';
import 'tinymce/themes/modern/theme';
import 'tinymce/plugins/link';
import 'tinymce/plugins/autolink';
import 'tinymce/plugins/image';
import 'tinymce/plugins/lists';

import 'tinymce-i18n/langs/fr_FR';

require.context(
  'file-loader?name=[path][name].[ext]&context=node_modules/tinymce!tinymce/skins',
  true,
  /.*/
);

module.exports = function (selector) {
  tinymce.init({
    selector,
    plugins: 'link autolink image lists',
    toolbar: 'bold italic | formatselect | link image | bullist numlist',
    menubar: false,
    statusbar: false,
    language: 'fr_FR',
    block_formats: 'Paragraphe=p;Titre=h2;Sous-titre=h3;Petit titre=h4'
  });
};
