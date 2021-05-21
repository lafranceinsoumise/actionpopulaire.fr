import styled from "styled-components";
import PropTypes from "prop-types";
import React, { useCallback, useEffect, useRef, useState } from "react";

import ResultBox from "./ResultBox";
import { InfosElu } from "./types";
import defaultAxios from "axios";
import { useDebounce } from "../../../lib/components/utils/hooks";
import AnimatedMoreHorizontal from "../../../front/components/genericComponents/AnimatedMoreHorizontal";
import ScrollableBlock from "./ScrollableBlock";
import { chercherElus } from "./queries";

const SearchInputLayout = styled.div`
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
export const SearchInput = ({ onInput }) => (
  <SearchInputLayout>
    <input
      type="text"
      name="recherche"
      placeholder="Rechercher un⋅e élu, une commune..."
      onInput={onInput}
    />
  </SearchInputLayout>
);
SearchInput.propTypes = { onInput: PropTypes.func };
SearchInput.defaultTypes = { onInput: () => {} };

const SELECTEUR_STATES = {
  MONTRER_ELUS_PROCHES: "montrer-elus-proches",
  ATTENTE_REQUETE: "attente-requete",
  MONTRER_RESULTATS: "montrer-resultats-recherche",
  ERREUR_REQUETE: "erreur-requete",
};

const Message = styled.div`
  margin: 2em 2em;
`;

const SelecteurElusLayout = styled.section`
  display: flex;
  flex-direction: column;

  border-right: 2px solid ${(props) => props.theme.black100};

  ${ScrollableBlock.Layout} {
    flex-grow: 1;
  }

  ${ResultBox.Layout} {
    border-top: 10px solid ${(props) => props.theme.black50};
  }

  @media (max-width: ${(props) => props.theme.collapse}px) {
    width: 100%;
  }

  .loader {
    margin: 2em auto;
  }
`;
export const SelecteurElus = ({
  elusAContacter,
  elusProches,
  elusRecherche,
  selection,
  onSelect,
  onSearchResults,
}) => {
  const [state, setState] = useState(SELECTEUR_STATES.MONTRER_ELUS_PROCHES);

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
      const results = await chercherElus(q, cancelSource.token);
      // ce test permet de gérer la situation (normalement rare) où la requête a été annulée
      // après que la requête se soit terminée mais avant qu'on ai mis à jour les résultats
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
        setState(SELECTEUR_STATES.MONTRER_ELUS_PROCHES);
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
    <SelecteurElusLayout>
      <SearchInput onInput={inputCallback} />
      {state === SELECTEUR_STATES.ATTENTE_REQUETE ? (
        <div className="loader">
          <AnimatedMoreHorizontal />
        </div>
      ) : state === SELECTEUR_STATES.ERREUR_REQUETE ? (
        <Message>
          Une erreur inattendue a été rencontrée. Retentez votre recherche.
        </Message>
      ) : (
        <ScrollableBlock>
          {state === SELECTEUR_STATES.MONTRER_ELUS_PROCHES ? (
            elusAContacter.length === 0 && elusProches.length === 0 ? (
              <Message>
                <a href="/profil/identite/">Indiquez où vous êtes</a> pour voir
                les élus les plus proches de chez vous ou utilisez la recherche
                ci-dessus.
              </Message>
            ) : (
              <>
                <ResultBox
                  elus={elusAContacter}
                  selected={selection}
                  onSelect={onSelect}
                />
                <ResultBox
                  elus={elusProches}
                  selected={selection}
                  onSelect={onSelect}
                />
              </>
            )
          ) : elusRecherche.length === 0 ? (
            <Message>Aucun résultat pour votre recherche.</Message>
          ) : (
            <ResultBox
              elus={elusRecherche}
              selected={selection}
              onSelect={onSelect}
            />
          )}
        </ScrollableBlock>
      )}
    </SelecteurElusLayout>
  );
};

SelecteurElus.propTypes = {
  elusAContacter: PropTypes.arrayOf(InfosElu),
  elusProches: PropTypes.arrayOf(InfosElu),
  elusRecherche: PropTypes.arrayOf(InfosElu),
  selection: InfosElu,
  onSelect: PropTypes.func,
  onSearchResults: PropTypes.func,
};

SelecteurElus.Layout = SelecteurElusLayout;
