import React from "react";

import Spacer from "@agir/front/genericComponents/Spacer";

const Legal = () => {
  return (
    <p style={{ fontSize: "13px", color: "#777777" }}>
      <strong>Premier alinéa de l’article 11-4</strong> de la loi 88-227 du 11
      mars 1988 modifiée : une personne physique peut verser un don à un parti
      ou groupement politique si elle est de nationalité française ou si elle
      réside en France. Les dons consentis et les cotisations versées en qualité
      d’adhérent d’un ou de plusieurs partis ou groupements politiques par une
      personne physique dûment identifiée à une ou plusieurs associations
      agréées en qualité d’association de financement ou à un ou plusieurs
      mandataires financiers d’un ou de plusieurs partis ou groupements
      politiques ne peuvent annuellement excéder 7 500 euros.
      <Spacer size="0.5rem" />
      <strong>Troisième alinéa de l’article 11-4 :</strong> Les personnes
      morales à l’exception des partis ou groupements politiques ne peuvent
      contribuer au financement des partis ou groupements politiques, ni en
      consentant des dons, sous quelque forme que ce soit, à leurs associations
      de financement ou à leurs mandataires financiers, ni en leur fournissant
      des biens, services ou autres avantages directs ou indirects à des prix
      inférieurs à ceux qui sont habituellement pratiqués. Les personnes
      morales, à l’exception des partis et groupements politiques ainsi que des
      établissements de crédit et sociétés de financement ayant leur siège
      social dans un Etat membre de l’Union européenne ou partie à l’accord sur
      l’Espace économique européen, ne peuvent ni consentir des prêts aux partis
      et groupements politiques ni apporter leur garantie aux prêts octroyés aux
      partis et groupements politiques.
      <Spacer size="0.5rem" />
      <strong>Premier alinéa de l’article 11-5 :</strong> Les personnes qui ont
      versé un don ou consenti un prêt à un ou plusieurs partis ou groupements
      politiques en violation des articles 11-3-1 et 11-4 sont punies de trois
      ans d’emprisonnement et de 45 000 € d’amende.
    </p>
  );
};

export default Legal;
