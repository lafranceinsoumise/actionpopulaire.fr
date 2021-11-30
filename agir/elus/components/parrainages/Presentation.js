import React from "react";
import styled from "styled-components";

const LayoutExterieur = styled.main`
  height: 100%;
  display: flex;
  flex-direction: column;
  justify-content: center;
  align-items: center;
`;

const LayoutInterieur = styled.div`
  max-width: 600px;
  margin: 0 auto;
`;

const Presentation = () => (
  <LayoutExterieur>
    <LayoutInterieur>
      <img
        style={{ margin: "0 auto" }}
        src="/static/parrainages/recherche_parrainages.png"
        alt="Une femme qui tient trois formulaires de promesse de parrainage."
      />
      <h2>Collecte des parrainages</h2>
      <p>
        Interface d’organisation pour l’obtention des 500 signatures pour la
        candidature de Jean-Luc Mélenchon aux présidentielles de 2022.
      </p>
      <ol>
        <li>
          Choisissez un⋅e élu⋅e disponible, c'est-à-dire que personne d'autre
          n'a encore prévu de contacter
        </li>
        <li>
          Confirmez que vous comptez le ou la contacter. Ce sera votre
          responsabilité !
        </li>
        <li>
          Une fois que vous aurez rencontré l'élu, n'oubliez pas de nous
          indiquer la conclusion de l'échange dans cette même interface
        </li>
      </ol>
    </LayoutInterieur>
  </LayoutExterieur>
);

export default Presentation;
