import axios from 'axios';

function geoApi(url, fields, optionGetter) {
  return {
    query: nom => (
      axios.get(url, {params: {nom, fields}, headers: {'Accept': 'application/json'}}).then(
        res => ({options: res.data.map(optionGetter)}),
        () => {
          throw new Error('Problème de connexion.');
        }
      )
    ),
    reverse: code => (
      axios.get(url, {params: {code, fields}, headers: {'Accept': 'application/json'}}).then(
        res => optionGetter(res.data[0])
      )
    )
  };
}

const recupererCommunes = geoApi(
  'https://geo.api.gouv.fr/communes',
  'code,nom,departement',
  (commune) => ({value: commune.code, label: `${commune.nom} (${commune.departement.nom})`})
);


const recupererDepartements = geoApi(
  'https://geo.api.gouv.fr/departements',
  'code,nom',
  (departement) => ({value: departement.code, label: `${departement.nom} (${departement.code})`})
);


const communeDescriptor = {
  name: 'Commune',
  getter: recupererCommunes
};

const departementDescriptor = {
  name: 'Département',
  getter: recupererDepartements,
};

const regionDescriptor = {
  name: 'Région',
  values: [
    {label: 'Auvergne-Rhône-Alpes', value: '84'},
    {label: 'Bourgogne-Franche-Comté', value: '27'},
    {label: 'Bretagne', value: '53'},
    {label: 'Centre-Val de Loire', value: '24'},
    {label: 'Grand Est', value: '44'},
    {label: 'Guadeloupe', value: '01'},
    {label: 'Hauts-de-France', value: '32'},
    {label: 'Île-de-France', value: '11'},
    {label: 'Normandie', value: '28'},
    {label: 'Nouvelle-Aquitaine', value: '75'},
    {label: 'Occitanie', value: '76'},
    {label: 'Pays de la Loire', value: '52'},
    {label: 'Provence-Alpes-Côte d\'Azur', value: '93'},
    {label: 'La Réunion', value: '04'},
  ]
};

const arrondissementDescriptor = {
  name: 'Ville',
  values: ['Paris', 'Lyon', 'Marseille'].map(v => ({label: v, value: v}))
};

const collectiviteUniqueDescriptor = {
  name: 'Collectivité territoriale unique',
  values: [
    {label: 'Assemblée de Corse', value: 'corse-unique'},
    {label: 'Assemblée de Guyane', value: 'guyane-unique'},
    {label: 'Assemblée de Martinique', value: 'martinique-unique'},
    {label: 'Conseil départemental de Mayotte', value: 'mayotte-unique'},
  ]
};

const COMDescriptor = {
  name: 'Collectivité d\'outre mer',
  values: [
    {label: 'Assemblée de la Polynésie française', value: 'polynesie-francaise'},
    {label: 'Conseil territorial de Saint-Barthélémy', value: 'saint-barthelemy'},
    {label: 'Conseil territorial de Saint-Martin', value: 'saint-martin'},
    {label: 'Conseil territorial de Saint-Pierre-et-Miquelon', value: 'saint-pierre-et-miquelon'},
    {label: 'Assemblée territoriale des îles Wallis-et-Futuna', value: 'wallis-et-futuna'},
  ]
};

const provinceNouvelleCaledonieDescriptor = {
  name: 'Nom de l\'assemblée',
  values: [
    {label: 'Province Sud', value: 'sud'},
    {label: 'Province Nord', value: 'nord'},
    {label: 'Province des Îles Loyauté', value: 'iles-loyaute'}
  ]
};


export const mandateGroups = [
  {
    name: 'Mandats nationaux', mandates: [
      {id: 'depute', name: 'Député', division: null},
      {id: 'senateur', name: 'Sénateur', division: departementDescriptor},
      {id: 'depute-europeen', name: 'Député européen', division: null},
    ]
  },
  {
    name: 'Mandats régionaux', mandates: [
      {id: 'conseiller-regional', name: 'Conseiller régional', division: regionDescriptor},
    ]
  },
  {
    name: 'Mandats départementaux', mandates: [
      {id: 'conseiller-departemental', name: 'Conseiller départemental', division: departementDescriptor},
    ]
  },
  {
    name: 'Mandats municipaux', mandates: [
      {id: 'maire', name: 'Maire', division: communeDescriptor},
      {id: 'maire-adjoint', name: 'Maire adjoint', division: communeDescriptor},
      {id: 'conseiller-municipal', name: 'Conseiller municipal', division: communeDescriptor},
    ]
  },
  {
    name: 'Mandats Paris / Lyon / Marseille', mandates: [
      {id: 'conseiller-paris', name: 'Conseiller de Paris', division: null},
      {id: 'conseiller-metropole-lyon', name: 'Conseiller métropolitain de Lyon', division: null},
      {id: 'maire-arrondissement', name: 'Maire d\'arrondissement', division: arrondissementDescriptor},
      {
        id: 'maire-adjoint-arrondissement',
        name: 'Maire adjoint  d\'arrondissement',
        division: arrondissementDescriptor
      },
      {id: 'conseiller-arrondissement', name: 'Conseiller  d\'arrondissement', division: arrondissementDescriptor}
    ]
  },
  {
    name: 'Autres mandats locaux', mandates: [
      {
        id: 'elu-collectivite-unique',
        name: 'Elu d\'une collectivité territoriale unique',
        division: collectiviteUniqueDescriptor
      },
      {id: 'elu-collectivite-outre-mer', name: 'Élu d\'une collectivité d\'outre-mer', division: COMDescriptor},
      {id: 'elu-congres-nouvelle-caledonie', name: 'Élu au congrès de la Nouvelle-Calédonie', division: null},
      {
        id: 'elu-province-nouvelle-caledonie',
        name: 'Élu d\'une assemblée de province de Nouvelle-Calédonie',
        division: provinceNouvelleCaledonieDescriptor
      }
    ]
  },
  {
    name: 'Mandats Français de l\'étranger', mandates: [
      {id: 'conseiller-afe', name: 'Conseiller à l\'Assemblée des Français de l\'Étranger (AFE)', division: null},
      {id: 'conseiller-consulaire', name: 'Conseiller consulaire', division: null}
    ]
  }
];

export const mandateDict = {};

for (let group of mandateGroups) {
  for (let type of group.mandates) {
    mandateDict[type.id] = type;
  }
}

