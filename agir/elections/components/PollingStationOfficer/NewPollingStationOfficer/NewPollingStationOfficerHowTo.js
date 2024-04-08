import React from "react";

import Button from "@agir/front/genericComponents/Button";
import Link from "@agir/front/app/Link";
import Spacer from "@agir/front/genericComponents/Spacer";
import { MailTo } from "@agir/elections/Common/StyledComponents";

const NewPollingStationOfficerHowTo = () => (
  <div>
    <h2>Devenir assesseur·e ou délégué·e</h2>
    <Spacer size="0.5rem" />
    <p>
      <strong>
        Pour la réussite de ce scrutin, il est nécessaire que nous ayons un
        maximum d'assesseur⋅es et de délégué⋅es dans le plus grand nombre de
        bureaux de vote.
      </strong>
    </p>
    <Spacer size="1rem" />
    <p>
      La tenue d’un bureau de vote est un temps particulier mais néanmoins très
      important de la campagne électorale. Les assesseur·es et délégué·es se
      doivent de contribuer au bon déroulement du scrutin dans chaque bureau de
      vote toute la journée mais aussi à l’heure du dépouillement.
    </p>
    <Spacer size="1rem" />
    <p>
      <strong>
        Il s’agit pour nous de faire respecter les règles de transparence et
        d’organisation prévues par le Code électoral.
      </strong>
    </p>
    <Spacer size="1rem" />
    <p>
      C’est à chaque scrutin que nous devons garder les bonnes habitudes et
      surtout faire en sorte qu’elles ne se perdent pas. En effet les
      &laquo;&nbsp;ententes à la bonne franquette&nbsp;&raquo; sur le thème nous
      &laquo;&nbsp;avons toujours fait comme ça&nbsp;&raquo; sont à bannir dès
      lors qu’elles rentrent en contradiction avec le <em>Code électoral</em>.
    </p>
    <Spacer size="1rem" />
    <div
      css={`
        font-size: 0.875rem;
        background-color: ${({ theme }) => theme.primary50};
        padding: 1rem;
        border-radius: ${({ theme }) => theme.borderRadius};

        strong {
          font-weight: 600;
        }
      `}
    >
      <strong
        css={`
          color: ${({ theme }) => theme.primary500};
        `}
      >
        Quel est le rôle des délégué·e·s et assesseur·es&nbsp;?
      </strong>
      <Spacer size="0.5rem" />
      <strong>
        Durant le scrutin vous pouvez être amené·e en tant que délégué·e ou
        assesseur·e à saisir le/la Président·e de bureau d’une irrégularité.
      </strong>
      <Spacer size="0.5rem" />
      Vous aurez aussi à mobiliser le/la représentant·e local·e pour qu’il/elle
      intervienne par écrit séance tenante auprès du Préfet pour obtenir des
      rappels à la Loi et le cas échéant&nbsp;:
      <Spacer size="0.5rem" />
      <ul>
        <li>la visite du ou de la représentant·e du Conseil constitutionnel</li>
        <li>
          le juge aux élections dans les communes de plus de 20 000
          habitant·e·s, obligatoirement de permanence sur votre département
        </li>
      </ul>
      <Spacer size="0.5rem" />
      Le jour du vote, pour assurer un bon déroulement du scrutin, privilégions
      la désignation d’assesseur·es ou, à défaut, de délégué·e·s. Les seconds
      n’ont qu’un rôle d’observation et de rappel à la loi électorale. Ils ne
      sont pas membres du bureau de vote.
      <Spacer size="1rem" />
      <strong
        css={`
          color: ${({ theme }) => theme.primary500};
        `}
      >
        Ressources pour les assesseur·es et délégué·es
      </strong>
      <Spacer size=".75rem" />
      <span
        css={`
          display: inline-flex;
          gap: 0.5rem;

          @media (max-width: ${({ theme }) => theme.collapse}px) {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
          }
        `}
      >
        <Button
          link
          small
          color="primary"
          icon="youtube"
          href="https://www.youtube.com/watch?v=b2ocgH48-1Q"
          target="_blank"
          rel="noopener noreferrer"
        >
          La vidéo de formation
        </Button>
        <Button
          link
          small
          color="primary"
          icon="file-text"
          route="pollingStationOfficerGuide"
          target="_blank"
          rel="noopener noreferrer"
        >
          Le guide PDF
        </Button>
      </span>
    </div>
    <Spacer size="1.5rem" />
    <h5>Contactez les équipes de campagne près de chez vous</h5>
    <Spacer size="0.5rem" />
    <p>
      Remplissez ce formulaire pour prendre contact avec les équipes de campagne
      près de chez vous pour qu'un travail collectif de désignation des
      assesseur·es et délégué·es puisse être mis en place&nbsp;!
    </p>
    <Spacer size="1.5rem" />
    <p
      css={`
        color: ${(props) => props.theme.black500};
      `}
    >
      ⏱️ Durée du formulaire&nbsp;:&nbsp;4 minutes
    </p>
  </div>
);

export default NewPollingStationOfficerHowTo;
