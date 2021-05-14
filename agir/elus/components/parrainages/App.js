import React, { useCallback, useReducer } from "react";
import styled from "styled-components";
import FicheElu from "@agir/elus/parrainages/FicheElu";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Logo from "@agir/front/allPages/TopBar/Logo";
import style from "@agir/front/genericComponents/_variables.scss";
import { SelecteurElus } from "./SelecteurElus";
import { ELU_STATUTS } from "./types";
import ScrollableBlock from "./ScrollableBlock";
import PropTypes from "prop-types";
import { useIsDesktop } from "../../../front/components/genericComponents/grid";

const ACTION_TYPES = {
  CHANGER_STATUT: "changer-statut",
  RESULTATS_RECHERCHE: "resultats-recherche",
  SELECTION: "selection",
};

const initialState = () => {
  const elusInitiauxScript = document.getElementById("elusInitiaux");
  let elusInitiaux = { proches: [], aContacter: [] };

  if (elusInitiauxScript && elusInitiauxScript.type === "application/json") {
    elusInitiaux = JSON.parse(elusInitiauxScript.textContent);
  }

  return {
    elusAContacter: elusInitiaux.aContacter,
    elusProches: elusInitiaux.proches,
    elusRecherche: [],
    selection: null,
  };
};

const reducer = (state, action) => {
  console.log(state, action);
  if (action.type === ACTION_TYPES.CHANGER_STATUT) {
    const { elusAContacter, elusProches, elusRecherche, selection } = state;
    const nouvelElu = action.elu;

    return {
      // on l'ajoute ou on le retire de la liste des élus à contacter selon le statut
      elusAContacter:
        nouvelElu.statut === ELU_STATUTS.A_CONTACTER
          ? [nouvelElu, ...elusAContacter]
          : elusAContacter.filter((e) => e.id !== nouvelElu.id),
      // On le retire de la liste des élus proches (dans aucun cas un nouvel élu
      // ne peut rejoindre cette liste !)
      elusProches: elusProches.filter((e) => e.id !== nouvelElu.id),
      // On intervertit le nouvel élu s'il était présent dans la liste des élus recherche
      elusRecherche: elusRecherche.map((e) =>
        e.id === nouvelElu.id ? nouvelElu : e
      ),
      selection: selection.id === nouvelElu.id ? nouvelElu : selection,
    };
  } else if (action.type === ACTION_TYPES.RESULTATS_RECHERCHE) {
    return {
      ...state,
      elusRecherche: action.resultats,
    };
  } else if (action.type === ACTION_TYPES.SELECTION) {
    return {
      ...state,
      selection: action.elu,
    };
  }

  return state;
};

const HeaderLayout = styled.nav`
  flex-grow: 0;
  padding: 0.75rem 2rem;

  background-color: #fff;

  display: flex;
  justify-content: space-between;
  margin: 0;

  @media (max-width: ${+style.collapse - 1}px) {
    padding: 1rem 1.5rem;
  }
  
  border-bottom: 2px solid ${style.black100};
  
  align:items: center;

  > a {
    display: flex;
    align-items: center;
    justify-content: center;
  }

  > *:nth-child(2) {
    flex-grow: 1;    
  }
`;
const Header = ({ onClose }) => {
  const isDesktop = useIsDesktop();
  const backCallback = useCallback(
    (e) => {
      if (isDesktop || onClose === null) return;

      e.preventDefault();
      onClose();
    },
    [isDesktop, onClose]
  );

  return (
    <HeaderLayout>
      <a href="/" aria-label="Retour" onClick={backCallback}>
        <FeatherIcon name="arrow-left" color={style.black1000} />
      </a>
      <a href="/" aria-label="Action populaire">
        <Logo />
      </a>
    </HeaderLayout>
  );
};
Header.propTypes = { onClose: PropTypes.func };

const Layout = styled.div`
  display: flex;
  flex-direction: column;

  font-size: 14px;
  line-height: 1.7;

  margin: 0;
  padding: 0;
  height: 100vh;
  max-height: 100vh;
  overflow: hidden;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    margin-top: -56px;
  }
`;

const MainLayout = styled.main`
  display: flex;
  align-items: stretch;
  flex-grow: 1;

  > ${SelecteurElus.Layout} {
    width: 470px;
  }

  > ${ScrollableBlock.Layout} {
    flex-grow: 1;
  }

  @media (max-width: ${(props) => props.theme.collapse}px) {
    position: relative;

    > ${SelecteurElus.Layout} {
      width: 100%;
    }

    > ${ScrollableBlock.Layout} {
      background-color: #fff;

      display: none;

      &.selection {
        display: block;
        position: absolute;
        top: 0;
        right: 0;
        bottom: 0;
        left: 0;
      }
    }
  }
`;

const App = () => {
  const [state, dispatch] = useReducer(reducer, null, initialState);
  console.log(state);

  return (
    <Layout>
      <Header
        onClose={
          state.selection &&
          (() => dispatch({ type: ACTION_TYPES.SELECTION, elu: null }))
        }
      />
      <MainLayout>
        <SelecteurElus
          {...state}
          onSearchResults={(resultats) =>
            dispatch({
              type: ACTION_TYPES.RESULTATS_RECHERCHE,
              resultats,
            })
          }
          onSelect={(elu) => dispatch({ type: ACTION_TYPES.SELECTION, elu })}
        />
        <ScrollableBlock className={state.selection ? "selection" : ""}>
          <FicheElu
            elu={state.selection}
            onStatusChange={(elu) => {
              dispatch({
                type: ACTION_TYPES.CHANGER_STATUT,
                elu,
              });
            }}
          />
        </ScrollableBlock>
      </MainLayout>
    </Layout>
  );
};

App.propTypes = {};

export default App;
