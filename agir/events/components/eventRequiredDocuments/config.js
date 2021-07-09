import imgDocA from "./images/doc_A.jpg";
import imgDocB from "./images/doc_B.jpg";
import imgDocC from "./images/doc_C.jpg";
import imgDocD from "./images/doc_D.jpg";

export const EVENT_DOCUMENT_TYPES = {
  A: {
    type: "A",
    image: imgDocA,
    name: "Attestation de concours en nature",
    templateLink: "#",
    description:
      "Nécessaire lorsque vous empruntez n’importe quel matériel, comme une sono, un barnum, une estrade, un rétro-projecteur, etc.",
  },
  B: {
    type: "B",
    image: imgDocB,
    name: "Attestation de règlement des consommations",
    templateLink: "#",
    description:
      "Certifie que les consommations ont été réglées directement à l'établissement par les participants, et non par l'organisateur⋅rice de l'événement.",
  },
  C: {
    type: "C",
    image: imgDocC,
    name: "Attestation pour les salles municipales",
    templateLink: "#",
    description:
      "Cette attestation est nécessaire pour certifier que la mise à disposition de la salle municipale est gratuite et s'adresse à toutes les autres forces politiques et leurs candidats. Elle doit vous être délivrée par la mairie.",
  },
  D: {
    type: "D",
    image: imgDocD,
    name: "Copie de la demande d'autorisation d'occupation de l'espace public",
    templateLink: "#",
    description:
      "Ce document est nécessaire lorsque vous organisez une manifestation, une réunion publique extérieure, ou encore un pique-nique, un apéro citoyen ou une table militante.",
  },
};
