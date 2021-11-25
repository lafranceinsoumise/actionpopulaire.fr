import React, { useReducer } from "react";
import styled, { ThemeProvider } from "styled-components";
import ScrollableBlock from "./ScrollableBlock";
import BarreSuperieure from "./BarreSuperieure";
import Presentation from "./Presentation";
import FicheElu from "./FicheElu";
import Menu from "./Menu";

import style from "@agir/front/genericComponents/_variables.scss";
import {
  ACTION_TYPES,
  initialState,
  reducer,
} from "@agir/elus/parrainages/reducer";

const LayoutExterieur = styled.div`
  display: flex;
  flex-direction: column;

  font-size: 14px;
  line-height: 1.7;

  margin: 0;
  padding: 0;
  height: 100vh;
  max-height: 100vh;
  overflow: hidden;
`;

const LayoutInterieur = styled.main`
  display: flex;
  align-items: stretch;
  flex-grow: 1;

  position: relative;

  > ${Menu.Layout} {
    width: 470px;
  }

  > ${ScrollableBlock.Layout} {
    flex-grow: 1;
  }

  @media (max-width: ${(props) => props.theme.collapse}px) {
    position: relative;

    > ${Menu.Layout} {
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

  return (
    <ThemeProvider theme={style}>
      <LayoutExterieur>
        <BarreSuperieure
          onClose={
            state.selection &&
            (() => dispatch({ type: ACTION_TYPES.SELECTION, elu: null }))
          }
        />
        <LayoutInterieur>
          <Menu
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
            {state.selection ? (
              <FicheElu
                elu={state.selection}
                onStatusChange={(elu) => {
                  dispatch({
                    type: ACTION_TYPES.CHANGER_STATUT,
                    elu,
                  });
                }}
              />
            ) : (
              <Presentation />
            )}
          </ScrollableBlock>
        </LayoutInterieur>
      </LayoutExterieur>
    </ThemeProvider>
  );
};

App.propTypes = {};

export default App;
