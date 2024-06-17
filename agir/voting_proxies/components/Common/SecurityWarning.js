import React, { useState } from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Link from "@agir/front/app/Link";

const Warning = () => {
  const [isCollapsed, setIsCollapsed] = useState(true);

  return (
    <div>
      <p>
        Pour répondre à un maximum de demandes, nous avons fait le choix de
        rendre notre espace procurations <strong>ouvert à tout le monde</strong>
        . Mais nous savons aussi que{" "}
        <strong>
          donner procuration à une personne inconnue est un acte de confiance
        </strong>
         : bien qu'un risque d'infiltration existe, nous faisons tout le
        possible pour qu'il reste marginal et pour réperer et limiter les abus
        {isCollapsed ? "..." : "."}
      </p>
      {!isCollapsed && (
        <>
          <p>
            La très grande majorité des nos volontaires sont des{" "}
            <strong>militant·es du mouvement</strong> et nous privilégions, lors
            de la mise en relation, les personnes avec le plus d'ancienneté dans
            le mouvement. Des mécanismes sont également en place pour{" "}
            <strong>bloquer les inscriptions en masse</strong>.
          </p>
          <p>
            Pour réduire encore plus les risques d'utilisation malveillante,
            nous vous conseillons, si vous le pouvez, d'échanger brièvement avec
            la personne volontaire ou de rechercher son nom et prénom sur
            internet pour vous faire vous-même une idée.
          </p>
          <p>Nous comptons aussi sur votre engagement !</p>
          <p>
            N'hésitez pas à nous signaler tout abus en nous écrivant à
            l'adresse :{" "}
            <strong>
              <Link href="mailto:procurations@actionpopulaire.fr">
                procurations@actionpopulaire.fr
              </Link>
            </strong>
          </p>
        </>
      )}
      {isCollapsed ? (
        <Button
          small
          inline
          color="link"
          icon="chevron-down"
          rightIcon
          onClick={() => setIsCollapsed(false)}
        >
          Voir plus
        </Button>
      ) : (
        <Button
          small
          inline
          color="link"
          icon="chevron-up"
          rightIcon
          onClick={() => setIsCollapsed(true)}
        >
          Voir moins
        </Button>
      )}
    </div>
  );
};

const SecurityWarning = styled(({ children, ...attrs }) => (
  <div {...attrs}>
    <FeatherIcon name="shield" />
    <Warning />
  </div>
))`
  padding: 1.5rem;
  background-color: ${({ theme, background }) => background || theme.primary50};
  display: flex;
  align-items: start;
  gap: 1rem;

  & > :first-child {
    flex: 0 0 auto;
    color: ${({ theme, iconColor }) => iconColor || theme.primary500};
  }

  & > div {
    margin: 0;
    display: flex;
    flex-flow: column nowrap;
    font-size: 0.875rem;

    & > p + p {
      margin-top: 0.5rem;
    }
  }

  ${Button} {
    align-self: end;
  }
`;

export default SecurityWarning;
