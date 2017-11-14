import icons from 'trumbowyg/dist/ui/icons.svg';
import 'trumbowyg/dist/ui/trumbowyg.min.css';
import 'trumbowyg/dist/trumbowyg';
import 'trumbowyg/dist/langs/fr.min';

$.trumbowyg.svgPath = icons;

import './richEditor.css';

module.exports = function (elem) {
    elem = $(elem);
    elem.trumbowyg({
        btnsDef: {
            titlesGroup: {
                dropdown: ['h2', 'h3', 'h4'],
                title: ['Titres'],
                ico: 'h2'
            }
        },
        btns: [
            ['strong', 'em'],
            'titlesGroup',
            ['link', 'insertImage'],
            ['unorderedList', 'orderedList'],
            ['removeFormat']
        ],
        'lang': 'fr',
        autogrow: true,
    });

    return {
        value: function() {
            return elem.trumbowyg.apply(elem, ['html'].concat(Array.prototype.slice.call(arguments)));
        }
    }
};
