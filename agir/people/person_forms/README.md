# Configuration des champs d'un formulaire personnalisé

Les champs d'un formulaire personnalisé sont définis à travers une configuration au format [JSON](https://www.json.org/json-fr.html). Il s'agit d'un tableau (array) de configurations de groupes de champs.

## Paramètres d'un groupe de champs

Un groupe de champs représente une section du formulaire. Pour chaque groupe de champs, on définit obligatoirement un titre et une liste de champs.
Un texte introductif peut aussi être ajouté entre le titre et les champs de la section.

##### Paramètres obligatoires

- `"title": "Informations personnelles" [string]`
  Le titre du groupe de champs

- `"fields": [...] [object[]]`
  Un tableau de configurations de champs de formulaire

##### Paramètres optionnels

- `"intro_html": "<h4>Informations nécessaires à l'envoi du document</h4>" [string]`
  Texte (au format HTML) à afficher sous le titre du groupe de champs

## Paramètres d'un champs de saisi de formulaire

Chaque champs dans un groupe de champs est défini par un objet au format JSON.
Certaines propriétés de cet objet sont spécifiques aux types de champs, alors que d'autres s'appliquent à tous les types.

### Paramètres communs à tous les types de champs

##### Paramètres obligatoires

- `"id": "prenom" [string]`
  L'identifiant court du champs qui sera utilisé pour enregistrer les valeurs renseignées par les utilisateur·ices pour le champs. Il doit être unique pour tout le formulaire.

- `"label": "Prénom" [string]`
  Le libellé du champs. Cette propriété est obligatoire uniquement si la propriété `person_field` (cf. [Paramètres optionnels](#parametres-optionnels)) n'est pas indiquée ou sa valeur est `false`.

- `"type": "short_text" [string]`
  Le type de champs à utiliser. Cette propriété est obligatoire uniquement si la propriété `person_field` (cf. [Paramètres optionnels](#parametres-optionnels)) n'est pas indiquée ou sa valeur est `false`. Les types de champs disponibles sont: ["short_text"](#short_text), ["long_text"](#long_text), ["choice"](#choice), ["radio_choice"](#radio_choice), ["autocomplete_choice"](#autocomplete_choice), ["autocomplete_multiple_choice"](#autocomplete_multiple_choice), ["multiple_choice"](#multiple_choice), ["email_address"](#email_address), ["phone_number"](#phone_number), ["url"](#url), ["file"](#file), ["boolean"](#boolean), ["integer"](#integer), ["decimal"](#decimal), ["datetime"](#datetime), ["date"](#date), ["multidate"](#date), ["person"](#person), ["iban"](#iban), ["commune"](#commune), ["group"](#group), ["multiple_groups"](#multiple_groups), ["newsletters"](#newsletters), ["event_theme"](#event_theme).

##### Paramètres optionnels

- `"person_field": true [boolean]`
  Si `true`, le champs sera automatiquement lié à une propriété (si celle-ci existe) de la personne connectée. Le champs sera pré-rempli et les informations de la personne mises à jour en cas de modification du champs. Si `false`, le champs ne sera pas lié à la personne connectée: il sera donc obligatoire de spécifié une valeur pour les propriétés `label` et `type`.

- `"required": false [boolean]`
  Cette propriété indique si le champs est obligatoire pour la soumission du formulaire ou non. Si non spécifié, sa valeur sera par défaut `true` pour les champs dont la propriété `person_field` est `true`, sinon `false`.

- `"disabled": false [boolean]`
  Cette propriété indique si le champs est modifiable par l'utilisateur (`false`) ou non (`true`).

- `"initial": "Un texte" [any]`
  La valeur initiale du champs (selon le type de champs).

##### Examples

```json
[
  {
    "id": "first_name",
    "person_field": true
  },
  {
    "id": "ice-cream-flavor",
    "label": "Parfum de glâce",
    "type": "short_text",
    "required": true,
    "disabled": false,
    "initial": "Pistache"
  }
]
```

### Types de champs et paramètres spécifiques

#### `short_text`

Un champs de saisie de texte court.

##### Paramètres obligatoires

_Ce type n'a pas de paramètres obligatoires spécifiques._

##### Paramètres optionnels

- `"min_length": 3 [number]`, `"max_length": 10 [number]`
  Le nombre de caractères minimum (`min_length`) et maximum (`max_length`) autorisé pour le champs.

- `"strip": true [boolean]`
  Indique si la valeur renseignées doit être enregistrée en supprimant les espaces au début et à la fin.

- `"choices": [["a", "Choix A"], ["b", "Choix B"]] [array[]]`
  Une liste de valeurs possibles à suggérer à la personne. Si cette propriété est indiqué, la personne pourra soit choisir parmi les valeurs suggérées, soit écrire une nouvelle valeur directement dans le champs. La valeur de cette propriété est un tableau en deux dimensions (tableau de tableaux) indiquant une liste de choix possibles et, pour chaque choix, la valeur (toute expression JSON valide est acceptée) suivie du libellé du choix (string).

##### Examples

```json
{
  "id": "ice-cream-flavor",
  "label": "Parfum de glâce",
  "type": "short_text",
  "choices": [
    ["Ba", "Banane"],
    ["Ch", "Chocolat"],
    ["Cr", "Crème"]
  ],
  "min_length": "3",
  "max_length": "255",
  "strip": true
}
```

#### `long_text`

Un champs de saisie de texte long.

##### Paramètres obligatoires

_Ce type n'a pas de paramètres obligatoires spécifiques._

##### Paramètres optionnels

- `"min_length": 3 [number]`, `"max_length": 10 [number]`
  Le nombre de caractères minimum (`min_length`) et maximum (`max_length`) autorisé pour le champs.

- `"strip": true [boolean]`
  Indique si la valeur renseignées doit être enregistrée en supprimant les espaces au début et à la fin.

##### Examples

```json
{
  "id": "haiku",
  "label": "Haïku",
  "type": "long_text",
  "min_length": "3",
  "max_length": "255",
  "strip": true
}
```

#### `choice`

Un champs qui permet le choix parmi plusieurs valeurs prédéfinies grâce à une liste déroulante. Une seule valeur peut-être sélectionnée.

##### Paramètres obligatoires

- `"choices": [["a", "Choix A"], ["b", "Choix B"]] [array[] / string[]]`
  La liste de valeurs possibles.
  La valeur de cette propriété peut être:
  1. un tableau de valeurs (string) - ex. `"choices": ["a", "b", "c"]`
  2. un tableau en deux dimensions (tableau de tableaux) indiquant une liste de choix possibles et, pour chaque choix, la valeur (toute expression JSON valide est acceptée) suivie du libellé du choix (string)
  3. un tableau en trois dimensions pour présenter une liste du type 2 séparé en sous-listes - ex. `"choices": [["Catégorie A", [["a", "choix A"]]]]`

##### Paramètres optionnels

- `"default_label": "---" [string]`
  Le libellé de la valeur vide, lorsqu'aucune option n'est sélectionnée

##### Examples

```js
[
  {
    "id": "app_1",
    "label": "Appartement",
    "type": "choice",
    "default_label": "Je ne vis pas ici", // Libellé de la valeur vide ("")
    "choices": ["1A", "1B", "2A", "2B"] // Uniquement les valeurs (utilisées aussi comme libellés)
  },
  {
    "id": "app_2",
    "label": "Appartement",
    "type": "choice",
    "choices": [
      [
        "1A", // Valeur enregistrée
        "App. 1A" // Libellé du choix
      ],
      ["1B", "App. 1B"],
      ["2A", "App. 2A"],
      ["2B", "App. 2B"]
    ]
  },
  {
    "id": "app_3",
    "label": "Appartement",
    "type": "choice",
    "choices": [
      [
        "1er étage", // Libellé de la catégorie de choix
        [
          [
            "1A", // Valeur enregistrée
            "App. 1A" // Libellé du choix
          ],
          ["1B", "App. B"]
        ]
      ],
      [
        "2ème étage",
        [
          ["2A", "App. A"],
          ["2B", "App. B"]
        ]
      ]
    ]
  }
];
```

#### `radio_choice`

Un champs qui permet le choix parmi plusieurs valeurs prédéfinies à des cases à cocher de type radio. Une seule valeur peut-être sélectionnée.

##### Paramètres obligatoires

- `"choices": [["a", "Choix A"], ["b", "Choix B"]] [array[] / string[]]`
  La liste de valeurs possibles. La valeur de cette propriété peut être:
  1. un tableau de valeurs (string) - ex. `"choices": ["a", "b", "c"]`
  2. un tableau en deux dimensions (tableau de tableaux) indiquant une liste de choix possibles et, pour chaque choix, la valeur (toute expression JSON valide est acceptée) suivie du libellé du choix (string)

##### Examples

```json
[
  {
    "id": "app_1",
    "label": "Appartement",
    "type": "radio_choice",
    "choices": ["1A", "1B", "2A", "2B"]
  },
  {
    "id": "app_2",
    "label": "Appartement",
    "type": "radio_choice",
    "choices": [
      ["1A", "App. 1A"],
      ["1B", "App. 1B"],
      ["2A", "App. 2A"],
      ["2B", "App. 2B"]
    ]
  }
]
```

#### `autocomplete_choice`

Un champs qui permet le choix parmi plusieurs valeurs prédéfinies grâce à une liste déroulante filtrable. Une seule valeur peut-être sélectionnée.

##### Paramètres obligatoires

- `"choices": [["a", "Choix A"], ["b", "Choix B"]] [array[] / string[]]`
  La liste de valeurs possibles.
  La valeur de cette propriété peut être:
  1. un tableau de valeurs (string) - ex. `"choices": ["a", "b", "c"]`
  2. un tableau en deux dimensions (tableau de tableaux) indiquant une liste de choix possibles et, pour chaque choix, la valeur (toute expression JSON valide est acceptée) suivie du libellé du choix (string)
  3. un tableau en trois dimensions pour présenter une liste du type 2 séparé en sous-listes - ex. `"choices": [["Catégorie A", [["a", "choix A"]]]]`

##### Paramètres optionnels

- `"default_label": "---" [string]`
  Le libellé de la valeur vide, lorsqu'aucune option n'est sélectionnée

##### Examples

```json
[
  {
    "id": "app_1",
    "label": "Appartement",
    "type": "autocomplete_choice",
    "default_label": "Je ne vis pas ici",
    "choices": ["1A", "1B", "2A", "2B"]
  },
  {
    "id": "app_2",
    "label": "Appartement",
    "type": "autocomplete_choice",
    "default_label": "Je ne vis pas ici",
    "choices": [
      ["1A", "App. 1A"],
      ["1B", "App. 1B"],
      ["2A", "App. 2A"],
      ["2B", "App. 2B"]
    ]
  },
  {
    "id": "app_3",
    "label": "Appartement",
    "type": "autocomplete_choice",
    "default_label": "Je ne vis pas ici",
    "choices": [
      [
        "1er étage",
        [
          ["1A", "App. A"],
          ["1B", "App. B"]
        ]
      ],
      [
        "2ème étage",
        [
          ["2A", "App. A"],
          ["2B", "App. B"]
        ]
      ]
    ]
  }
]
```

#### `autocomplete_multiple_choice`

Un champs qui permet le choix parmi plusieurs valeurs prédéfinies grâce à une liste déroulante filtrable. Plusieurs valeurs peuvent être sélectionnées.

##### Paramètres obligatoires

- `"choices": [["a", "Choix A"], ["b", "Choix B"]] [array[] / string[]]`
  La liste de valeurs possibles. La valeur de cette propriété peut être:
  1. un tableau de valeurs (string) - ex. `"choices": ["a", "b", "c"]`
  2. un tableau en deux dimensions (tableau de tableaux) indiquant une liste de choix possibles et, pour chaque choix, la valeur (toute expression JSON valide est acceptée) suivie du libellé du choix (string)
  3. un tableau en trois dimensions pour présenter une liste du type 2 séparé en sous-listes - ex. `"choices": [["Catégorie A", [["a", "choix A"]]]]`

##### Paramètres optionnels

- `"max_items": 3 [number]`
  Le nombre de choix maximum autorisé.

##### Examples

```json
[
  {
    "id": "app_1",
    "label": "Appartement",
    "type": "autocomplete_multiple_choice",
    "max_items": 2,
    "choices": ["1A", "1B", "2A", "2B"]
  },
  {
    "id": "app_2",
    "label": "Appartement",
    "type": "autocomplete_multiple_choice",
    "max_items": 2,
    "choices": [
      ["1A", "App. 1A"],
      ["1B", "App. 1B"],
      ["2A", "App. 2A"],
      ["2B", "App. 2B"]
    ]
  },
  {
    "id": "app_3",
    "label": "Appartement",
    "type": "autocomplete_multiple_choice",
    "max_items": 2,
    "choices": [
      [
        "1er étage",
        [
          ["1A", "App. A"],
          ["1B", "App. B"]
        ]
      ],
      [
        "2ème étage",
        [
          ["2A", "App. A"],
          ["2B", "App. B"]
        ]
      ]
    ]
  }
]
```

#### `multiple_choice`

Un champs qui permet le choix parmi plusieurs valeurs prédéfinies grâce à une liste déroulante. Plusieurs valeurs peuvent être sélectionnées.

##### Paramètres obligatoires

- `"choices": [["a", "Choix A"], ["b", "Choix B"]] [array[] / string[]]`
  La liste de valeurs possibles. La valeur de cette propriété peut être:
  1. un tableau de valeurs (string) - ex. `"choices": ["a", "b", "c"]`
  2. un tableau en deux dimensions (tableau de tableaux) indiquant une liste de choix possibles et, pour chaque choix, la valeur (toute expression JSON valide est acceptée) suivie du libellé du choix (string)

##### Examples

```json
[
  {
    "id": "app_1",
    "label": "Appartement",
    "type": "multiple_choice",
    "choices": ["1A", "1B", "2A", "2B"]
  },
  {
    "id": "app_2",
    "label": "Appartement",
    "type": "multiple_choice",
    "choices": [
      ["1A", "App. 1A"],
      ["1B", "App. 1B"],
      ["2A", "App. 2A"],
      ["2B", "App. 2B"]
    ]
  }
]
```

#### `email_address`

Un champs qui permet la saisie et la validation d'une adresse e-mail.

##### Paramètres obligatoires

_Ce type n'a pas de paramètres obligatoires spécifiques._

##### Examples

```json
{
  "id": "email",
  "label": "Adresse e-mail",
  "type": "email_address"
}
```

#### `phone_number`

Un champs qui permet la saisie et la validation d'un numéro de téléphone.

##### Paramètres obligatoires

_Ce type n'a pas de paramètres obligatoires spécifiques._

##### Paramètres optionnels

- `"region": "EE" [string]`
  Le code [ISO_3166-1](https://en.wikipedia.org/wiki/ISO_3166-1#Current_codes) de la région par défaut du numéro de téléphone

##### Examples

```json
{
  "id": "phone",
  "label": "Numéro de téléphone",
  "type": "phone_number",
  "region": "FR"
}
```

#### `url`

Un champs qui permet la saisie et la validation d'un URL.

##### Paramètres obligatoires

_Ce type n'a pas de paramètres obligatoires spécifiques._

##### Examples

```json
{
  "id": "website-url",
  "label": "URL du site web",
  "type": "url"
}
```

#### `file`

Un champs qui permet l'ajout d'un fichier en pièce-jointe du formulaire.

##### Paramètres obligatoires

_Ce type n'a pas de paramètres obligatoires spécifiques._

##### Paramètres optionnels

- `"max_size": 1024 [number]`
  La taille maximale autorisée du fichier (en octets)

- `"allowed_extensions": ["jpg", "png"] [string[]]`
  Les extensions de fichier autorisées

- `"multiple": false [boolean]`
   Autoriser ou non l'envoi de plusieurs fichiers

##### Examples

```json
{
  "id": "profile-picture",
  "label": "Photo de profil",
  "type": "file",
  "max_size": 1000000,
  "allowed_extensions": ["jpg", "png"],
  "multiple": false
}
```

#### `boolean`

Un champs qui permet d'afficher une case à cocher.

##### Paramètres obligatoires

_Ce type n'a pas de paramètres obligatoires spécifiques._

##### Examples

```json
{
  "id": "consent",
  "label": "J'accepte les conditions générales",
  "type": "boolean"
}
```

#### `integer`

Un champs qui permet de saisir un nombre entier.

##### Paramètres obligatoires

_Ce type n'a pas de paramètres obligatoires spécifiques._

##### Paramètres optionnels

- `"min_value": 3 [number]`, `"max_value": 10 [number]`
  La valeur minimum et maximum autorisée pour le champs.

##### Examples

```json
{
  "id": "participants",
  "label": "Nombre de participants",
  "type": "integer",
  "min_value": 1,
  "max_value": 500
}
```

#### `decimal`

Un champs qui permet de saisir un nombre décimal.

##### Paramètres obligatoires

_Ce type n'a pas de paramètres obligatoires spécifiques._

##### Paramètres optionnels

- `"min_value": 3 [number]`, `"max_value": 10 [number]`
  La valeur minimum et maximum autorisée pour le champs.

- `"max_digits": 3 [number]`
  La valeur maximal de chiffre du nombre saisi

- `"decimal_places": 2 [number]`
  Le nombre maximum de chiffres après la virgule

##### Examples

```json
{
  "id": "price",
  "label": "Prix de vente",
  "type": "decimal",
  "min_value": 1,
  "max_value": 50,
  "max_digits": 4,
  "decimal_places": 2
}
```

#### `datetime`

Un champs qui permet de saisir une date et un horaire.

##### Paramètres obligatoires

_Ce type n'a pas de paramètres obligatoires spécifiques._

##### Examples

```json
{
  "id": "birthdate",
  "label": "Date et heure de naissance",
  "type": "datetime"
}
```

#### `date`

Un champs qui permet de saisir une date.

##### Paramètres obligatoires

_Ce type n'a pas de paramètres obligatoires spécifiques._

##### Paramètres optionnels

- `"min_value": "1871-05-21" [string]`, `"max_value": "1871-05-28" [string]`
  La valeur minimum et maximum autorisée pour le champs.

##### Examples

```json
{
  "id": "date",
  "label": "Date",
  "type": "date",
  "min_value": "1871-05-21",
  "max_value": "1871-05-28"
}
```
#### `multidate`

Un champs qui permet de saisir une liste de dates.

##### Paramètres obligatoires

_Ce type n'a pas de paramètres obligatoires spécifiques._

##### Paramètres optionnels

- `"min_value": "1871-05-21" [string]`, `"max_value": "1871-05-28" [string]`
  La valeur minimale et maximale autorisée pour le champs. Il est possible d'indiquer une date exacte, ou bien une date relative (en anglais, ex. *'today', '2 years ago', '2 weeks from now'*).

- `"min_length": 1 [number]`, `"max_length": 10 [number]`
  La longeur minimale et maximale de la liste

- `"min_delta": 1 [number]`, `"max_delta": 10 [number]`
  La différence minimale et maximale entre la première et la dernière date de la liste (en jours).

##### Examples

```json
{
  "id": "dates",
  "type": "multidate",
  "label": "Dates disponibles",
  "initial": "1871-05-21",
  "required": false,
  "min_value": "1871-05-21",
  "max_value": "1871-05-28",
  "min_length": 2,
  "max_length": 3,
  "min_delta": 3,
  "max_delta": 5
}
```

#### `person`

Un champs qui permet de sélectionner un·e utilisateur·ice en saisissant son adresse e-mail

##### Paramètres obligatoires

_Ce type n'a pas de paramètres obligatoires spécifiques._

##### Paramètres optionnels

- `"allow_self": false [boolean]`
  Autoriser l'utilisateur·ice à s'auto-sélectionner

- `"allow_inactive": false [boolean]`
  Autoriser la sélection d'une personne inactive

##### Examples

```json
{
  "id": "new-manager",
  "label": "Nouvelle animatrice",
  "type": "person",
  "allow_self": true,
  "allow_inactive": false
}
```

#### `iban`

Un champs qui permet d'indiquer et valider un IBAN (International Bank Account Number)

##### Paramètres obligatoires

_Ce type n'a pas de paramètres obligatoires spécifiques._

##### Paramètres optionnels

- `"allowed_countries": ["FR"] [string[]]`
  Les codes des pays pour lesquels la saisie d'un IBAN est autorisée

##### Examples

```json
{
  "id": "iban",
  "label": "IBAN",
  "type": "iban",
  "allowed_countries": ["FR"]
}
```

#### `commune`

Un champs qui permet de rechercher et sélectionner une commune française.

##### Paramètres obligatoires

_Ce type n'a pas de paramètres obligatoires spécifiques._

##### Paramètres optionnels

- `"types": ["COM"] [string[]]`
  Les codes des types de communes à utiliser pour filtrer les résultats de recherche. Par défaut, tous les types seront affichés.
  Les valeurs disponibles sont:
  - "COM" (commune)
  - "ARM" (arrondissement municipal)
  - "COMA" (commune associée)
  - "COMD" (commune déléguée)
  - "SRM" (secteur électoral).

##### Examples

```json
{
  "id": "commune",
  "label": "Nom de la commune",
  "type": "commune",
  "types": ["SRM"]
}
```

#### `group`

Un champs qui permet de rechercher et sélectionner un seul groupe d'action à l'aide d'une liste déroulante.

##### Paramètres obligatoires

_Ce type n'a pas de paramètres obligatoires spécifiques._

##### Paramètres optionnels

- `"choices": "member" [string, string[]]`
  Une liste de valeurs possibles à suggérer à la personne. Les valeurs possibles sont :
  1. `"membre", "member"`, pour afficher tous les groupes dont la personne est membre
  2. `"animateur", "animatrice", "animator", "referent"` pour afficher tous les groupes dont la personne est animateur·ice
  3. `"manager", "gestionnaire"` pour afficher tous les groupes dont la personne est gestionnaire
  4. un tableau d'identifiants de groupe - ex. `"choices": ["64ed1c08-6329-4bee-aaae-c3d6a1ca0ec7", "3a32fc55-7507-4d5f-bb57-a66daad63461"]`. La valeur par défaut est `membre`

##### Examples

```json
[
  {
    "id": "a-groupe",
    "label": "Mon groupe",
    "type": "group",
    "choices": "membre"
  },
  {
    "id": "b-groupe",
    "label": "Mon groupe",
    "type": "group",
    "choices": "animatrice"
  },
  {
    "id": "c-groupe",
    "label": "Mon groupe",
    "type": "group",
    "choices": "gestionnaire"
  },
  {
    "id": "d-groupe",
    "label": "Mon groupe",
    "type": "group",
    "choices": [
      "64ed1c08-6329-4bee-aaae-c3d6a1ca0ec7",
      "3a32fc55-7507-4d5f-bb57-a66daad63461"
    ]
  }
]
```

#### `multiple_groups`

Un champs qui permet de sélectionner plusieurs groupes d'action à l'aide d'une liste de case à cocher.

##### Paramètres obligatoires

- `"choices": "member" [string, string[]]`
  Une liste de valeurs possibles à suggérer à la personne. Les valeurs possibles sont :
  1. `"membre", "member"`, pour afficher tous les groupes dont la personne est membre
  2. `"animateur", "animatrice", "animator", "referent"` pour afficher tous les groupes dont la personne est animateur·ice
  3. `"manager", "gestionnaire"` pour afficher tous les groupes dont la personne est gestionnaire
  4. un tableau d'identifiants de groupe - ex. `"choices": ["64ed1c08-6329-4bee-aaae-c3d6a1ca0ec7", "3a32fc55-7507-4d5f-bb57-a66daad63461"]`. La valeur par défaut est `membre`

##### Examples

```json
[
  {
    "id": "a-groupe",
    "label": "Mon groupe",
    "type": "multiple_groups",
    "choices": "membre"
  },
  {
    "id": "b-groupe",
    "label": "Mon groupe",
    "type": "multiple_groups",
    "choices": "animatrice"
  },
  {
    "id": "c-groupe",
    "label": "Mon groupe",
    "type": "multiple_groups",
    "choices": "gestionnaire"
  },
  {
    "id": "d-groupe",
    "label": "Mon groupe",
    "type": "multiple_groups",
    "choices": [
      "64ed1c08-6329-4bee-aaae-c3d6a1ca0ec7",
      "3a32fc55-7507-4d5f-bb57-a66daad63461"
    ]
  }
]
```

#### `newsletters`

Un champs qui permet de sélectionner une ou plusieurs newsletters parmi une liste de case à cocher.

##### Paramètres obligatoires

- `"choices": [["2022", "Newsletter 2022"]] [array[]]`
  Une liste de valeurs possibles à suggérer à la personne. La valeur de cette propriété est un tableau en deux dimensions (tableau de tableaux) indiquant une liste de choix possibles et, pour chaque choix, la valeur (l'identifiant d'une newsletter) suivie du libellé du choix (string). Par défaut toutes les newsletters disponibles sont affichées.


#### `event_theme`

Un champs qui permet de sélectionner un thème d'événement parmi ceux enregistrés dans l'admin.

##### Paramètres obligatoires

_Ce type n'a pas de paramètres obligatoires spécifiques._

##### Paramètres optionnels

- `"event_theme_type": null [string, number]`
  L'id (nombre) ou le nom (chaîne de caractères) d'un type de thème d'événement pour n'afficher que les thèmes appartenant à un type particulier

##### Examples

```json
{
  "id": "theme",
  "label": "Thème de l'événement",
  "type": "event_type",
  "event_theme_type": "Café populaire"
}
```



## Example

```json
[
  {
    "title": "Champs liés à la personne connectée",
    "intro_html": "<p>Ces champs sont liés à la personne connectée</p>",
    "fields": [
      {
        "id": "first_name",
        "person_field": true
      },
      {
        "id": "last_name",
        "person_field": true
      },
      {
        "id": "gender",
        "person_field": true
      }
    ]
  },
  {
    "title": "Champs 'short_text'",
    "intro_html": "<p>Champs de saisi d'un texte court</p>",
    "fields": [
      {
        "id": "ice-cream-flavor",
        "label": "Parfum de glâce",
        "type": "short_text",
        "choices": [
          ["Ba", "Banane"],
          ["Ch", "Chocolat"],
          ["Cr", "Crème"]
        ],
        "min_length": "3",
        "max_length": "255",
        "strip": true
      }
    ]
  },
  {
    "title": "Champs 'long_text'",
    "intro_html": "<p>Champs de saisi d'un texte sur plusieurs lignes</p>",
    "fields": [
      {
        "id": "haiku",
        "label": "Haïku",
        "type": "long_text",
        "min_length": "3",
        "max_length": "255",
        "strip": true
      }
    ]
  },
  {
    "title": "Champs 'choice'",
    "intro_html": "<p>Champs de sélection simple avec liste déroulante</p>",
    "fields": [
      {
        "id": "choice_1",
        "label": "Appartement",
        "type": "choice",
        "default_label": "Je ne vis pas ici",
        "choices": ["1A", "1B", "2A", "2B"]
      },
      {
        "id": "choice_2",
        "label": "Appartement",
        "type": "choice",
        "choices": [
          ["1A", "App. 1A" ],
          ["1B", "App. 1B"],
          ["2A", "App. 2A"],
          ["2B", "App. 2B"]
        ]
      },
      {
        "id": "choice_3",
        "label": "Appartement",
        "type": "choice",
        "choices": [
          [
            "1er étage",
            [
              ["1A", "App. 1A"],
              ["1B", "App. B"]
            ]
          ],
          [
            "2ème étage",
            [
              ["2A", "App. A"],
              ["2B", "App. B"]
            ]
          ]
        ]
      }
    ]
  },
  {
    "title": "Champs 'radio_choice'",
    "intro_html": "<p>Champs de sélection simple avec case à cocher</p>",
    "fields": [
      {
        "id": "radio_1",
        "label": "Appartement",
        "type": "radio_choice",
        "choices": ["1A", "1B", "2A", "2B"]
      },
      {
        "id": "radio_2",
        "label": "Appartement",
        "type": "radio_choice",
        "choices": [
          ["1A", "App. 1A"],
          ["1B", "App. 1B"],
          ["2A", "App. 2A"],
          ["2B", "App. 2B"]
        ]
      }
    ]
  },
  {
    "title": "Champs 'autocomplete_choice'",
    "intro_html": "<p>Champs de sélection simple avec recherche</p>",
    "fields": [
      {
        "id": "autocomplete_1",
        "label": "Appartement",
        "type": "autocomplete_choice",
        "default_label": "Je ne vis pas ici",
        "choices": ["1A", "1B", "2A", "2B"]
      },
      {
        "id": "autocomplete_2",
        "label": "Appartement",
        "type": "autocomplete_choice",
        "default_label": "Je ne vis pas ici",
        "choices": [
          ["1A", "App. 1A"],
          ["1B", "App. 1B"],
          ["2A", "App. 2A"],
          ["2B", "App. 2B"]
        ]
      },
      {
        "id": "autocomplete_3",
        "label": "Appartement",
        "type": "autocomplete_choice",
        "default_label": "Je ne vis pas ici",
        "choices": [
          [
            "1er étage",
            [
              ["1A", "App. A"],
              ["1B", "App. B"]
            ]
          ],
          [
            "2ème étage",
            [
              ["2A", "App. A"],
              ["2B", "App. B"]
            ]
          ]
        ]
      }
    ]
  },
  {
    "title": "Champs 'autocomplete_multiple_choice'",
    "intro_html": "<p>Champs de sélection multiple avec recherche</p>",
    "fields": [
      {
        "id": "autocomplete_multi_1",
        "label": "Appartement",
        "type": "autocomplete_multiple_choice",
        "max_items": 2,
        "choices": ["1A", "1B", "2A", "2B"]
      },
      {
        "id": "autocomplete_multi_2",
        "label": "Appartement",
        "type": "autocomplete_multiple_choice",
        "max_items": 2,
        "choices": [
          ["1A", "App. 1A"],
          ["1B", "App. 1B"],
          ["2A", "App. 2A"],
          ["2B", "App. 2B"]
        ]
      },
      {
        "id": "autocomplete_multi_3",
        "label": "Appartement",
        "type": "autocomplete_multiple_choice",
        "max_items": 2,
        "choices": [
          [
            "1er étage",
            [
              ["1A", "App. A"],
              ["1B", "App. B"]
            ]
          ],
          [
            "2ème étage",
            [
              ["2A", "App. A"],
              ["2B", "App. B"]
            ]
          ]
        ]
      }
    ]
  },
  {
    "title": "Champs 'multiple_choice'",
    "intro_html": "<p>Champs de sélection multiple avec cases à cocher</p>",
    "fields": [
      {
        "id": "multiple_choice_1",
        "label": "Appartement",
        "type": "multiple_choice",
        "choices": ["1A", "1B", "2A", "2B"]
      },
      {
        "id": "multiple_choice_2",
        "label": "Appartement",
        "type": "multiple_choice",
        "choices": [
          ["1A", "App. 1A"],
          ["1B", "App. 1B"],
          ["2A", "App. 2A"],
          ["2B", "App. 2B"]
        ]
      }
    ]
  },
  {
    "title": "Champs 'email_address'",
    "intro_html": "<p>Champs de saisie d'adresse e-mail</p>",
    "fields": [
      {
        "id": "email",
        "label": "Adresse e-mail",
        "type": "email_address"
      }
    ]
  },
  {
    "title": "Champs 'phone_number'",
    "intro_html": "<p>Champs de saisie de numéro de téléphone</p>",
    "fields": [
      {
        "id": "phone",
        "label": "Numéro de téléphone",
        "type": "phone_number",
        "region": "FR"
      }
    ]
  },
  {
    "title": "Champs 'url'",
    "intro_html": "<p>Champs d'URL</p>",
    "fields": [
      {
        "id": "website-url",
        "label": "URL du site web",
        "type": "url"
      }
    ]
  },
  {
    "title": "Champs 'file'",
    "intro_html": "<p>Champs d'ajout de fichier en pièce-jointe</p>",
    "fields": [
      {
        "id": "profile-picture",
        "label": "Photo de profil",
        "type": "file",
        "max_size": 1000000,
        "allowed_extensions": ["jpg", "png"],
        "multiple": false
      }
    ]
  },
  {
    "title": "Champs 'boolean'",
    "intro_html": "<p>Case à cocher</p>",
    "fields": [
      {
        "id": "consent",
        "label": "J'accepte les conditions générales",
        "type": "boolean"
      }
    ]
  },
  {
    "title": "Champs 'integer'",
    "intro_html": "<p>Champs de saisie d'un nombre entier</p>",
    "fields": [
      {
        "id": "participants",
        "label": "Nombre de participants",
        "type": "integer",
        "min_value": 1,
        "max_value": 500
      }
    ]
  },
  {
    "title": "Champs 'decimal'",
    "intro_html": "<p>Champs de saisie d'un nombre décimal</p>",
    "fields": [
      {
        "id": "price",
        "label": "Prix de vente",
        "type": "decimal",
        "min_value": 1,
        "max_value": 50,
        "max_digits": 4,
        "decimal_places": 2
      }
    ]
  },
  {
    "title": "Champs 'datetime'",
    "intro_html": "<p>Champs de saisie de date et horaire</p>",
    "fields": [
      {
        "id": "startdate",
        "label": "Date et heure de début",
        "type": "datetime"
      }
    ]
  },
  {
    "title": "Champs 'date'",
    "intro_html": "<p>Champs de saisie de date</p>",
    "fields": [
      {
        "id": "date",
        "label": "Date",
        "type": "date",
        "min_value": "1871-05-21",
        "max_value": "1871-05-28"
      }
    ]
  },
  {
    "title": "Champs 'multidate'",
    "intro_html": "<p>Champs de saisie de plusieurs dates</p>",
    "fields": [
        {
          "id": "dates",
          "type": "multidate",
          "label": "Dates disponibles",
          "initial": "1871-05-21",
          "required": false,
          "min_value": "1871-05-21",
          "max_value": "1871-05-28",
          "min_length": 2,
          "max_length": 3,
          "min_delta": 3,
          "max_delta": 5
        }
    ]
  },
  {
    "title": "Champs 'person'",
    "intro_html": "<p>Champs de choix d'un·e utilisateur·ice d'Action Populaire par e-mail</p>",
    "fields": [
      {
        "id": "new-manager",
        "label": "Nouvel·le animateur·ice",
        "type": "person",
        "allow_self": true,
        "allow_inactive": false
      }
    ]
  },
  {
    "title": "Champs 'iban'",
    "intro_html": "<p>Champs de saisie d'un IBAN</p>",
    "fields": [
      {
        "id": "iban",
        "label": "IBAN",
        "type": "iban",
        "allowed_countries": ["FR"]
      }
    ]
  },
  {
    "title": "Champs 'commune'",
    "intro_html": "<p>Champs de recherche et sélection d'une commune française</p>",
    "fields": [
      {
        "id": "srm",
        "label": "Nom du secteur électoral",
        "type": "commune",
        "types": ["SRM"]
      },
      {
        "id": "commune",
        "label": "Nom de la commune",
        "type": "commune"
      }
    ]
  },
  {
    "title": "Champs 'group'",
    "intro_html": "<p>Champs de sélection simple d'un groupe d'action</p>",
    "fields": [
      {
        "id": "a-groupe",
        "label": "Les groupes dont je suis membre",
        "type": "group",
        "choices": "membre"
      },
      {
        "id": "b-groupe",
        "label": "Les groupes dont je suis animateur·ice",
        "type": "group",
        "choices": "animatrice"
      },
      {
        "id": "c-groupe",
        "label": "Les groupes dont je suis gesionnaire",
        "type": "group",
        "choices": "gestionnaire"
      },
      {
        "id": "d-groupe",
        "label": "Groupe",
        "type": "group",
        "choices": [
          "64ed1c08-6329-4bee-aaae-c3d6a1ca0ec7",
          "3a32fc55-7507-4d5f-bb57-a66daad63461"
        ]
      }
    ]
  },
  {
    "title": "Champs 'multiple_groups'",
    "intro_html": "<p>Champs de sélection multiple de groupes d'action</p>",
    "fields": [
      {
        "id": "a-groupes",
        "label": "Les groupes dont je suis membre",
        "type": "multiple_groups",
        "choices": "membre"
      },
      {
        "id": "b-groupes",
        "label": "Les groupes dont je suis animateur·ice",
        "type": "multiple_groups",
        "choices": "animatrice"
      },
      {
        "id": "c-groupes",
        "label": "Les groupes dont je suis gesionnaire",
        "type": "multiple_groups",
        "choices": "gestionnaire"
      },
      {
        "id": "d-groupes",
        "label": "Groupe",
        "type": "multiple_groups",
        "choices": [
          "64ed1c08-6329-4bee-aaae-c3d6a1ca0ec7",
          "3a32fc55-7507-4d5f-bb57-a66daad63461"
        ]
      }
    ]
  },
  {
    "title": "Champs 'newsletters'",
    "intro_html": "<p>Champs de sélection multiple de newsletters</p>",
    "fields": [
      {
        "id": "liaison",
        "label": "Correspondant·e d'immeuble",
        "type": "newsletters",
        "choices": [["2022", "J'accepte d'être correspondant·e d'immeuble"]]
      },
      {
        "id": "nls",
        "label": "Newsletters",
        "type": "newsletters"
      }
    ]
  },
  {
    "title": "Champs 'event_type'",
    "intro_html": "<p>Champs de sélection de thème d'événement</p>",
    "fields": [
      {
        "id": "theme_w_name",
        "label": "Thème de l'événement (nom)",
        "type": "event_type",
        "event_theme_type": "Café populaire"
      },
      {
        "id": "theme_w_id",
        "label": "Thème de l'événement (id)",
        "type": "event_type",
        "event_theme_type": 1
      }
    ]
  },
]
```
