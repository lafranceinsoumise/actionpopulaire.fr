import React from "react";
import Spacer from "@agir/front/genericComponents/Spacer";

import attConImg from "./images/ATT-CON.jpg";
import attRegImg from "./images/ATT-REG.jpg";
import attGraImg from "./images/ATT-GRA.jpg";
import attEspImg from "./images/ATT-ESP.jpg";

const staticPath = "/static/front/modeles/";
const attConTemplate = `${staticPath}Attestation_concours_en_nature.pdf`;
const attRegTemplate = `${staticPath}Attestation_mise_a_disposition_etablissement.pdf`;
const attGraTemplate = `${staticPath}Attestation_salle_municipale.pdf`;

export const EVENT_DOCUMENT_TYPES = {
  "ATT-CON": {
    type: "ATT-CON",
    image: attConImg,
    name: "Attestation de concours en nature",
    templateLink: attConTemplate,
    description:
      "Nécessaire lorsque vous empruntez n’importe quel matériel, comme une sono, un barnum, une estrade, un rétro-projecteur, etc.",
  },
  "ATT-REG": {
    type: "ATT-REG",
    image: attRegImg,
    name: "Attestation de règlement des consommations (mise à disposition d'un établissement privé)",
    templateLink: attRegTemplate,
    description:
      "Certifie que les consommations ont été réglées directement à l'établissement par les participants, et non par l'organisateur⋅rice de l'événement.",
  },
  "ATT-GRA": {
    type: "ATT-GRA",
    image: attGraImg,
    name: "Attestation de mise à disposition gratuite de salle municipale",
    templateLink: attGraTemplate,
    description: (
      <>
        Cette attestation est nécessaire pour certifier que la mise à
        disposition de la salle municipale est gratuite et s'adresse à toutes
        les autres forces politiques et leurs candidats. Elle doit vous être
        délivrée par la mairie.
        <Spacer size=".5rem" />
        <strong>À noter&nbsp;:</strong> pour réserver une salle, il vous sera
        demandé de l’assurer ! Durant la campagne présidentielle, vous pourrez
        utiliser notre{" "}
        <a
          href="https://infos.actionpopulaire.fr/wp-content/uploads/2021/02/Attestation-2021-assurance-locative-LFI.pdf"
          target="_blank"
          rel="noopener noreferrer"
        >
          attestation d’assurance convergence responsabilité civile.
        </a>
      </>
    ),
  },
  "ATT-ESP": {
    type: "ATT-ESP",
    image: attEspImg,
    name: "Copie de la demande d'autorisation d'occupation de l'espace public",
    templateLink: "",
    description:
      "Ce document est nécessaire lorsque vous organisez une manifestation, une réunion publique extérieure, ou encore un pique-nique, un apéro citoyen ou une table militante.",
  },
};

export const EVENT_PROJECT_STATUS = {
  DFI: "pending",
  ECO: "pending",
  REN: "pending",

  CLO: "archived",
  FIN: "archived",

  REF: "refused",
};
