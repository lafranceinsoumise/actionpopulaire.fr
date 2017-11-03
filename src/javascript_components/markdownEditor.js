import woofmark from 'woofmark';
import domador from 'domador';
import megamark from 'megamark';

import translation from './markdownEditorTranslation';

import 'woofmark/dist/woofmark.min.css'
import './markdownEditor.css';

Object.assign(woofmark.strings, translation);

module.exports = function (textarea) {
    return woofmark(textarea, {
        html: false,
        parseMarkdown: megamark,
        parseHTML: domador,
        defaultMode: 'wysiwyg',
        render: {
            modes: function(button, id) {
                button.textContent = translation.buttons[id];
            }
        }
    });
};
