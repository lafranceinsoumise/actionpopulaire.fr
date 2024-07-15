# Action populaire

## Comment ajouter une nouvelle page à l'application

### Back-end

Il est possible d'ajouter une nouvelle route côté back-end avec une vue front-end associée dans le fichier `agir/front/urls.py`.

Voici un example pour la page de test des icônes FontAwesome, dont le chemin est [https://actionpopulaire.fr/test/fontawesome](https://actionpopulaire.fr/test/fontawesome) :

```py
urlpatterns = [
    # ...
    path(
        "test/fontawesome/",
        views.FontAwesomeTestView.as_view()
    )
    # ...
]
```

Des classes de vues génériques existent et peuvent être utilisées à partir du fichier `agir/front/views/views.py` :
- `BaseAppView` : la vue de base basée sur un composant React
- `BaseAppCachedView` : la vue de base avec du cache
- `BaseAppSoftAuthView` : une vue accessible avec une connexion de type _soft_ (connexion via un URL)
- `BaseAppHardAuthView` : une vue accessible avec une connexion de type _hard_ (connexion via un code reçu par email)

Ces classes peuvent être évidemment être utilisées comme base pour créer des classes de vue pour des pages spécifiques, toujours dans le même fichier. C'est le cas de la page FontAwesome et de la vue `FontAwesomeTestView`, qui permet de précharger dans l'HTML, la liste des icônes utilisées en base de données et les transmettre au composant React.

Dans d'autres cas on peut vouloir personnaliser les metadonnées de la page, précharger des endpoints API pour rendre le chargement de la page plus rapide, restreindre l'accès à certaines personnes ou autre.


### Front-end

L'application étant une _Single Page Application_, il existe également un router et une configuration de routage côté front-end.

Une fois la route ajouté côté back-end, il est donc nécessaire de l'ajouter aussi côté front-end, dans le fichier : `agir/front/components/app/routes.config.js`.

Chaque route est ici representée en JavaScript par un objet  `RouteConfig` à l'intérieur de l'objet `routeConfig` qui est ensuite utilisé partout dans l'application pour afficher tel ou tel composant ou pour générer les liens ou les redirections internes.

Voici à quoi les propriétés qu'il est possible définir pour une route :

```js
export const routeConfig = {
  // ...
  faIcons: new RouteConfig({
    // PROPRIÉTÉS OBLIGATOIRES

    // L'ID et la clé sont identiques et sont utilisés comme référence de cette page à travers l'application
    id: "faIcons",

    // Le chemin exact ou le pattern utilisé pour afficher cette page. L'ordre est important, la première définition correspondant à l'URL sera utilisée
    path: "/test/fontawesome/",

    // Si exact est égal à true, le chemin indiqué devra correspondre entièrement pour que le composant associé s'affiche. Si égal à false, le composant s'affichera aussi pour tous les URLS qui commencent par le chemin indiqué
    exact: true,

    // Le type d'autentication requis pour la page (NONE, SOFT ou HARD)
    neededAuthentication: AUTHENTICATION.NONE,

    // Le libellé de la page, utilisé dans les menus, les boutons arrière, ...
    label: "Icônes Font Awesome",

    // Le composant React principal de la page (peut ne pas être spécifié uniquement dans le cas d'une redirection)
    Component: RouteComponents.FaIcons,

    // PROPRIÉTÉS OPTIONNELLES
    // D'autres propriétés peuvent être définies et seront utilisées ensuite par le componsant de base (agir/front/components/app/Page.js) ou éventuellement par les composants spécifiques à chaque page. Ces propriétés ne sont pas obligatoires.

    // La propriété params permet de définir les valeurs par défaut des paramétres qui peuvent être utilisé dans le chemin indiqué, utilisées notamment lors de la génération des liens
    params: { eventPk: null, activePanel: null },

    // Les propriétés AnonymousComponent et anonymousConfig, permette de spécifier une configuration différente lorsqu'on accède à un chemin protégé de manière anonyme
    // Par défaut, la personne sera redirigée vers la page de connexion
    AnonymousComponent: RouteComponents.HomePage,
    anonymousConfig: {
      hasLayout: true,
    },

    // La propriété isPartial, permet d'indiquer si la route correspond uniquement à une partie d'une page dont le composant principal est spécifié dans une autre définition. Par exemple, sur la page d'un groupe d'action, une configuration partielle définit les routes du panneau de gestion
    // Valeur par défaut : false
    isPartial: false,

    // La propriété redirectTo permet de spécifier une route qui, au lieu d'afficher un composant, redirige vers une autre page / route
    redirectTo: (_, routeParams) => ({
      route: "eventDetails",
      routeParams,
      backLink: "eventMap",
      push: false,
    }),

    // La propriété hasLayout, indique si la page utilise ou non le layout du dashboard (en trois colonnes sur desktop comme pour la homepage)
    // Valeur par défaut: false
    hasLayout: false,

    // layoutProps permet de passer des propriétés spécifiques au composant Layout, cf. agir/front/components/app/Layout
    layoutProps: {
      $smallBackgroundColor: style.black25,
    },

    // La propriété keepScroll, indique si garder le niveau de scroll de la page précédente au chargement
    // Valeur par défaut : false
    keepScroll: false,

    // La propriété hideFeedbackButton indique si le bouton flottant qui permet d'accéder au formulaire d'avis s'affiche (false) ou non (true) sur une page
    // Valeur par défaut: false
    hideFeedbackButton: false,

    // La propriété hideTopBar indique si la barre de navigation en haut de l'application s'affiche (false) ou non (true) sur une page
    // Valeur par défaut: false
    hideTopBar: true,

    // La propriété appOnlyTopBar indique si la barre de navigation en haut de l'application s'affiche uniquement dans les applications mobiles (true) ou non (true)
    // Valeur par défaut: false
    appOnlyTopBar: true,

    // La propriété hideFooter, indique si cacher le footer ou pas
    // Valeur par défaut : false
    hideFooter: false,

    // La propriété hideFooterBanner, indique si cacher la bannière qui s'affiche sur le footer lorsque la personne n'est pas connectée à son compte
    // Valeur par défaut : false
    hideFooterBanner: false,

    // La propriété displayFooterOnMobileApp, indique si afficher le footer dans les applications mobile Android et iOS
    // Valeur par défaut : false
    displayFooterOnMobileApp: true,

    // La propriété backLink définit la cible du lien qui permet de revenir en arrière
    // Par défaut, la cible est la page d'accueil
    backLink: {
      route: "events",
      label: "Liste des événements",
      isProtected: true,
    },

    // La propriété topBarRightLink définit la cible du lien en haut à droite de l'application
    // Par défaut, on affiche l'avatar de la personne connectée qui, au clic, affiche un menu
    topBarRightLink: {
      label: notificationSettingRoute.label,
      to: notificationSettingRoute.getLink({ root: "activite" }),
      protected: true,
    },
  }),
  // ...
};
```

La fonction principale de chaque objet définissant une route est de lier un chemin ou un modèle de chemin au composant principal de telle ou telle page.

Par commodité ces composants sont importés dans le fichier `agir/front/components/app/routes.components.js` de manière _lazy_, càd que le code spécifique à chacun est chargé uniquement au moment où le composant est affiché la première fois.

```js
const Routes = {
  // ...
  FaIcons: lazy(
    () =>
      import(
        /* webpackChunkName: "r-faicons" */
        "@agir/front/genericComponents/FaIcons"
      ),
  ),
  // ...
}
```

Dans la plupart des cas, le composant principal contient uniquement le contenu principal de chaque page, les éléments communs à la plupart des pages (barre de navigation, footer, ...) étant ajoutés automatiquement ou cachés via la configuration de la route.

Voici le code du composant `FaIcons` utilisé pour la page des icônes FontAwesome :

```jsx
export const FaIcons = () => {
  const icons = useMemo(() => {
    const dataElement = document.getElementById("usedIcons");
    return dataElement && dataElement.type === "application/json"
      ? JSON.parse(dataElement.textContent).filter(Boolean)
      : usedIcons;
  }, []);

  return (
    <StyledPage>
      {icons.sort().map((icon) => (
        <Icon key={icon} icon={icon} />
      ))}
    </StyledPage>
  );
};

export default FaIcons;
```
