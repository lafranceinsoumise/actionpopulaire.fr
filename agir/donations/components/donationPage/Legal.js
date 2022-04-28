import PropTypes from "prop-types";
import React from "react";

import Spacer from "@agir/front/genericComponents/Spacer";

const Legal = ({ type }) => (
  <p style={{ fontSize: "13px", color: "#777777" }}>
    {type === "2022" ? (
      <>
        Les dons sont destinés à l'
        <strong>
          <abbr title="Association de Financement de la Campagne Présidentielle de Jean-Luc Mélenchon 2022">
            AFCP JLM 2022
          </abbr>
        </strong>
        , déclarée à la préfecture de Paris le 15 juin 2021, seule habilitée à
        recevoir les dons en faveur du candidat Jean-Luc Mélenchon, dans le
        cadre de la campagne pour l'élection présidentielle de 2022.
        <Spacer size="0.5rem" />
        Un reçu détaché d'une formule numérotée éditée par la Commission
        nationale des comptes de campagne vous sera directement adressé en mai
        de l’année suivant l’année de versement de votre don.
        <Spacer size="0.5rem" />
        Tout don de personne morale (entreprise, association, SCI, compte
        professionnel de professions libérales ou de commerçants…) est interdit.
        <Spacer size="0.5rem" />
        <strong>
          Alinéa 1, 2 et 3 de l'article L. 52-8 du Code électoral :
        </strong>
        <Spacer size="0.5rem" />
        Une personne physique peut verser un don à un candidat si elle est de
        nationalité française ou si elle réside en France. Les dons consentis
        par une personne physique dûment identifiée pour le financement de la
        campagne d'un ou plusieurs candidats lors des mêmes élections ne peuvent
        excéder 4 600 euros. Les personnes morales, à l'exception des partis ou
        groupements politiques, ne peuvent participer au financement de la
        campagne électorale d'un candidat, ni en lui consentant des dons sous
        quelque forme que ce soit, ni en lui fournissant des biens, services ou
        autres avantages directs ou indirects à des prix inférieurs à ceux qui
        sont habituellement pratiqués. [...] Tout don de plus de 150 euros
        consenti à un candidat en vue de sa campagne doit être versé par chèque,
        virement, prélèvement automatique ou carte bancaire.
        <Spacer size="0.5rem" />
        <strong>III. de l'article L113-1 du Code électoral :</strong>
        <Spacer size="0.5rem" />
        Sera puni de trois ans d'emprisonnement et de 45 000 € d'amende
        quiconque aura, en vue d'une campagne électorale, accordé un don ou un
        prêt en violation des articles L. 52-7-1 et L. 52-8.
      </>
    ) : (
      <>
        <strong>Premier alinéa de l’article 11-4</strong> de la loi 88-227 du 11
        mars 1988 modifiée : une personne physique peut verser un don à un parti
        ou groupement politique si elle est de nationalité française ou si elle
        réside en France. Les dons consentis et les cotisations versées en
        qualité d’adhérent d’un ou de plusieurs partis ou groupements politiques
        par une personne physique dûment identifiée à une ou plusieurs
        associations agréées en qualité d’association de financement ou à un ou
        plusieurs mandataires financiers d’un ou de plusieurs partis ou
        groupements politiques ne peuvent annuellement excéder 7 500 euros.
        <Spacer size="0.5rem" />
        <strong>Troisième alinéa de l’article 11-4 :</strong> Les personnes
        morales à l’exception des partis ou groupements politiques ne peuvent
        contribuer au financement des partis ou groupements politiques, ni en
        consentant des dons, sous quelque forme que ce soit, à leurs
        associations de financement ou à leurs mandataires financiers, ni en
        leur fournissant des biens, services ou autres avantages directs ou
        indirects à des prix inférieurs à ceux qui sont habituellement
        pratiqués. Les personnes morales, à l’exception des partis et
        groupements politiques ainsi que des établissements de crédit et
        sociétés de financement ayant leur siège social dans un Etat membre de
        l’Union européenne ou partie à l’accord sur l’Espace économique
        européen, ne peuvent ni consentir des prêts aux partis et groupements
        politiques ni apporter leur garantie aux prêts octroyés aux partis et
        groupements politiques.
        <Spacer size="0.5rem" />
        <strong>Premier alinéa de l’article 11-5 :</strong> Les personnes qui
        ont versé un don ou consenti un prêt à un ou plusieurs partis ou
        groupements politiques en violation des articles 11-3-1 et 11-4 sont
        punies de trois ans d’emprisonnement et de 45 000 € d’amende.
      </>
    )}
  </p>
);

Legal.propTypes = {
  type: PropTypes.string,
};

export default Legal;
