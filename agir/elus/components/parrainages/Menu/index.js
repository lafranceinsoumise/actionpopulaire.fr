import styled from "styled-components";
import PropTypes from "prop-types";
import React, { useCallback, useEffect, useRef, useState } from "react";

import SelecteurElus from "./SelecteurElus";
import { InfosElu } from "../types";
import defaultAxios from "axios";
import { useDebounce } from "@agir/lib/utils/hooks";
import AnimatedMoreHorizontal from "@agir/front/genericComponents/AnimatedMoreHorizontal";
import ScrollableBlock from "../ScrollableBlock";
import { chercherElus, chercherCodePostal } from "../queries";
import Onglets from "./Onglets";

const CODE_POSTAL_REGEX = /^\d{5}$/;

const BoiteRechercheLayout = styled.div`
  flex-grow: 0;
  background-color: white;
  margin: 0;
  padding: 0.5rem 10px;
  display: flex;

  input {
    flex-grow: 1;
    margin: 0;
    padding: 1rem;
    background-color: ${(props) => props.theme.black50};
    border-radius: 0.5rem;
    border: none;
  }
`;
export const BoiteRecherche = ({ onInput }) => (
  <BoiteRechercheLayout>
    <input
      type="text"
      name="recherche"
      placeholder="Rechercher un code postal, un⋅e élu, une commune..."
      onInput={onInput}
    />
  </BoiteRechercheLayout>
);
BoiteRecherche.propTypes = { onInput: PropTypes.func };
BoiteRecherche.defaultTypes = { onInput: () => {} };

const SELECTEUR_STATES = {
  MONTRER_ONGLETS: "montrer-onglets",
  ATTENTE_REQUETE: "attente-requete",
  MONTRER_RESULTATS: "montrer-resultats-recherche",
  ERREUR_REQUETE: "erreur-requete",
};
const ONGLETS = {
  PROCHES: "Proches",
  EN_COURS: "En cours",
  TERMINES: "Terminées",
};

const MESSAGE_VIDE = {
  PROCHES: (
    <>
      <a href="/profil/identite/">Indiquez où vous êtes</a> pour voir les élus
      les plus proches de chez vous ou utilisez la recherche ci-dessus.
    </>
  ),
  EN_COURS: (
    <>
      Vous n'avez pas encore sélectionné de maires à rencontrer. Utilisez la
      barre de recherche ou regardez qui sont les maires les plus proches de
      chez vous !
    </>
  ),
  TERMINES: (
    <>
      Les maires que vous avez rencontré et pour lesquels vous avez renseigné le
      résultat de votre démarche s'afficheront ici, pour vous permettre de
      mettre à jour les informations en cas de démarche supplémentaire.
    </>
  ),
};

const MESSAGE_INTRO = {
  PROCHES: (
    <>
      Voici les élus les plus proches de votre adresse personnelle.{" "}
      <strong>
        Utilisez la barre de recherche ci-dessus pour rechercher un code postal,
        une commune, un maire...
      </strong>
    </>
  ),
  EN_COURS: (
    <>
      Voici les élus que vous avez prévu de rencontrer. N'oubliez pas de revenir
      indiquer le résultat de vos efforts !
    </>
  ),
  TERMINES: (
    <>
      Voici les élus que vous avez précédemment rencontrés. Si la situation a
      par la suite évolué, n'oubliez pas de le signaler ici !
    </>
  ),
};

const Message = styled.div`
  margin: 2em 2em;
`;

const MenuLayout = styled.section`
  display: flex;
  flex-direction: column;

  border-right: 2px solid ${(props) => props.theme.black100};

  ${ScrollableBlock.Layout} {
    flex-grow: 1;
  }

  ${SelecteurElus.Layout} {
    border-top: 10px solid ${(props) => props.theme.black50};
  }

  @media (max-width: ${(props) => props.theme.collapse}px) {
    width: 100%;
  }

  .loader {
    margin: 2em auto;
  }
`;
export const Menu = ({
  elusAContacter,
  elusTermines,
  elusProches,
  elusRecherche,
  selection,
  onSelect,
  onSearchResults,
}) => {
  const elusAccesRapide = {
    PROCHES: elusProches,
    EN_COURS: elusAContacter,
    TERMINES: elusTermines,
  };

  const [state, setState] = useState(SELECTEUR_STATES.MONTRER_ONGLETS);
  const [ongletActif, setOngletActif] = useState("PROCHES");

  // sentinelle utilisée pour identifier la dernière requête réalisée
  const lastRequestCancelSource = useRef(null);

  // Lance la recherche après un débouncing
  // À l'issue de la requête, les résultats ne sont mis à jour
  // que si aucune autre requête
  const recherche = useDebounce(async (q) => {
    const cancelSource = defaultAxios.CancelToken.source();
    lastRequestCancelSource.current = cancelSource;
    setState(SELECTEUR_STATES.ATTENTE_REQUETE);
    try {
      const results = q.match(CODE_POSTAL_REGEX)
        ? await chercherCodePostal(q, cancelSource.token)
        : await chercherElus(q, cancelSource.token);
      // ce test permet de gérer la situation (normalement rare) où la requête a été annulée
      // après que la requête se soit terminée mais avant qu'on ait mis à jour les résultats
      if (cancelSource === lastRequestCancelSource.current) {
        onSearchResults(results);
        setState(SELECTEUR_STATES.MONTRER_RESULTATS);
      }
    } catch (e) {
      if (cancelSource === lastRequestCancelSource.current) {
        console.log(e.message);
        setState(SELECTEUR_STATES.ERREUR_REQUETE);
      }
    }
  }, 600);

  const inputCallback = useCallback(
    async (e) => {
      if (lastRequestCancelSource.current) {
        lastRequestCancelSource.current.cancel();
        lastRequestCancelSource.current = null;
      }
      if (e.target.value === "") {
        recherche.cancel();
        setState(SELECTEUR_STATES.MONTRER_ONGLETS);
      } else {
        recherche(e.target.value);
      }
    },
    [recherche]
  );

  useEffect(() => {
    // On doit annuler les requêtes en cours et le débounce au démontage
    // (ou si la fonction de recherche change !)
    return () => {
      if (lastRequestCancelSource.current) {
        lastRequestCancelSource.current.cancel();
        lastRequestCancelSource.current = null;
      }
      recherche.cancel();
    };
  }, [recherche]);

  return (
    <MenuLayout>
      <BoiteRecherche onInput={inputCallback} />
      {state === SELECTEUR_STATES.ATTENTE_REQUETE ? (
        <div className="loader">
          <AnimatedMoreHorizontal />
        </div>
      ) : state === SELECTEUR_STATES.ERREUR_REQUETE ? (
        <Message>
          Une erreur inattendue a été rencontrée. Retentez votre recherche.
        </Message>
      ) : state === SELECTEUR_STATES.MONTRER_ONGLETS ? (
        <>
          <Onglets
            onglets={ONGLETS}
            actif={ongletActif}
            onChange={setOngletActif}
          />
          {elusAccesRapide[ongletActif].length === 0 ? (
            <ScrollableBlock>
              <Message>{MESSAGE_VIDE[ongletActif]}</Message>
            </ScrollableBlock>
          ) : (
            <ScrollableBlock>
              <Message>{MESSAGE_INTRO[ongletActif]}</Message>
              <SelecteurElus
                elus={elusAccesRapide[ongletActif]}
                selected={selection}
                onSelect={onSelect}
              />
            </ScrollableBlock>
          )}
        </>
      ) : elusRecherche.length === 0 ? (
        <Message>Aucun résultat pour votre recherche.</Message>
      ) : (
        <ScrollableBlock>
          <SelecteurElus
            elus={elusRecherche}
            selected={selection}
            onSelect={onSelect}
          />
        </ScrollableBlock>
      )}
    </MenuLayout>
  );
};

Menu.propTypes = {
  elusAContacter: PropTypes.arrayOf(InfosElu),
  elusTermines: PropTypes.arrayOf(InfosElu),
  elusProches: PropTypes.arrayOf(InfosElu),
  elusRecherche: PropTypes.arrayOf(InfosElu),
  selection: InfosElu,
  onSelect: PropTypes.func,
  onSearchResults: PropTypes.func,
};

Menu.Layout = MenuLayout;

export default Menu;
