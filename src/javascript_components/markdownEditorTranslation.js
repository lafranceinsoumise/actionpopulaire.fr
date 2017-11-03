module.exports = {
    placeholders: {
        bold: 'texte en gras',
        italic: 'texte en italique',
        quote: 'citation',
        code: 'code informatique',
        listitem: 'élément de liste',
        heading: 'titre',
        link: 'texte du lien',
        image: 'description de l\'image',
        attachment: 'description de la pièce jointe'
    },
    titles: {
        bold: 'Gras <strong> Ctrl+B',
        italic: 'Italique <em> Ctrl+I',
        quote: 'Citation <blockquote> Ctrl+J',
        code: 'Code <pre><code> Ctrl+E',
        ol: 'Liste numérotée <ol> Ctrl+O',
        ul: 'Liste simple <ul> Ctrl+U',
        heading: 'Titre <h1>, <h2>, ... Ctrl+D',
        link: 'Lien <a> Ctrl+K',
        image: 'Image <img> Ctrl+G',
        attachment: 'Pièce jointe Ctrl+Shift+K',
        markdown: 'Mode Markdown Ctrl+M',
        html: 'Mode HTML Ctrl+H',
        wysiwyg: 'Editeur Ctrl+P'
    },
    buttons: {
        bold: 'G',
        italic: 'I',
        quote: '«»',
        code: '</>',
        ol: '1.',
        ul: '\u29BF',
        heading: 'Tt',
        link: 'Lien',
        image: 'Image',
        attachment: 'Pièce jointe',
        hr: '\u21b5',
        wysiwyg: 'Editeur riche',
        markdown: 'Mode Markdown'
    },
    prompts: {
        link: {
            title: 'Insérer un lien',
            description: 'Entrez ou copiez l\'URL de votre lien',
            placeholder: 'http://exemple.fr/ "titre"'
        },
        image: {
            title: 'Insérer une image',
            description: 'Entrez ou copiez l\'URL de votre image',
            placeholder: 'http://exemple.fr/public/image.png "titre"'
        },
        attachment: {
            title: 'Ajouter une pièce jointe',
            description: 'Entrez ou copiez l\'URL de votre pièce jointe',
            placeholder: 'http://exemple.fr/public/rapport.pdf "titre"'
        },
        types: 'Vous pouvez seulement télécharger ',
        browse: 'Parcourir...',
        drophint: 'Vous pouvez aussi glisser-déposer des fichiers depuis votre ordinateur !',
        drop: 'Déposer votre fichier ici pour commencer le téléchargement...',
        upload: ', ou télécharger un fichier',
        uploading: 'Téléchargement de votre fichier...',
        uploadfailed: 'Votre téléchargement a échoué !'
    },
    modes: {
        wysiwyg: 'Editeur',
        markdown: 'Markdown',
    },
};