import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import InlineMenu from "@agir/front/genericComponents/InlineMenu";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import badDocument from "@agir/donations/spendingRequest/images/bad_doc.jpg";
import goodDocument from "@agir/donations/spendingRequest/images/good_doc.jpg";

const StyledMenuTrigger = styled.button`
  background: transparent;
  border: none;
  color: ${style.primary500};
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  text-align: left;

  &:hover,
  &:focus {
    text-decoration: underline;
  }

  @media (max-width: ${style.collapse}px) {
    font-size: 0.875rem;
    align-items: start;
  }

  ${RawFeatherIcon} {
    outline: none;
    width: 1rem;
    height: 1rem;

    @media (max-width: ${style.collapse}px) {
      margin-top: 3px;
    }
  }
`;

const StyledInlineMenu = styled.div`
  padding: 0 1rem;
  display: inline-grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  width: 100%;
  max-width: 600px;
  font-size: 0.875rem;

  @media (max-width: ${style.collapse}px) {
    padding: 1.5rem;
    grid-template-columns: repeat(auto-fill, minmax(275px, 1fr));
    max-width: 100%;
  }

  ul {
    padding-left: 1em;
  }

  article {
    padding: 0;
  }
`;

export const HELP_CONFIG = {
  documentTypes: {
    trigger: "Quels types de documents sont recevables ?",
    menu: (
      <>
        <article>
          <h5>Ce qui peut être une pièce comptable</h5>
          <ul>
            <li>Ticket de caisse (pas le reçu de carte bancaire)</li>
            <li>Devis</li>
            <li>
              Facture pro-forma (c'est-à-dire avant qu'elle ne soit acquittée)
            </li>
            <li>Justificatif de transport</li>
          </ul>
        </article>
        <article>
          <h5>Ce qui peut être un complément de justificatif</h5>
          <ul>
            <li>Photographie de l'événement</li>
            <li>
              Impression : <abbr title="Bon à tirer">BAT</abbr>, photographie
              des impressions, tract au format PDF
            </li>
            <li>
              Capture d'écran de la page de l'événement sur Action populaire ou
              du visuel de l'événement
            </li>
          </ul>
        </article>
      </>
    ),
  },
  documentQuality: {
    trigger:
      "Envoyez de préférence des documents numériques ou scannés : ils doivent être lisibles (exemple)",
    menu: (
      <>
        <article style={{ textAlign: "center" }}>
          <RawFeatherIcon
            name="x-circle"
            width="2.5rem"
            height="2.5rem"
            strokeWidth={1}
            style={{ color: style.redNSP }}
          />
          <h5 style={{ textTransform: "uppercase" }}>
            Exemple de document illisible
          </h5>
          <figure>
            <figcaption>
              Lettres manquantes ou floues, trop de contraste...
            </figcaption>
            <img src={badDocument} alt="Exemple de document illisible" />
          </figure>
        </article>
        <article style={{ textAlign: "center" }}>
          <RawFeatherIcon
            name="check-circle"
            width="2.5rem"
            height="2.5rem"
            strokeWidth={1}
            style={{ color: style.green500 }}
          />
          <h5 style={{ textTransform: "uppercase" }}>
            Exemple de document lisible
          </h5>
          <figure>
            <figcaption>Les articles, montants et dates sont nets</figcaption>
            <img src={goodDocument} alt="Exemple de document lisible" />
          </figure>
        </article>
      </>
    ),
  },
};

const SpendingRequestHelp = ({ helpId }) => {
  if (!helpId || !HELP_CONFIG[helpId]) {
    return null;
  }

  const { trigger, menu } = HELP_CONFIG[helpId];

  return (
    <InlineMenu
      Trigger={StyledMenuTrigger}
      triggerTextContent={trigger}
      triggerIconName="help-circle"
      position="bottom-left"
      hasCloseButton
    >
      <StyledInlineMenu>{menu}</StyledInlineMenu>
    </InlineMenu>
  );
};

SpendingRequestHelp.propTypes = {
  helpId: PropTypes.oneOf(Object.keys(HELP_CONFIG)),
};

export default SpendingRequestHelp;
