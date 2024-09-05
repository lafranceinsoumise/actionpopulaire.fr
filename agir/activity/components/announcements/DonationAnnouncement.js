import React from "react";
import styled from "styled-components";

import { Button } from "@agir/donations/common/StyledComponents";

const StyledWrapper = styled.div`
  background-color: ${(props) => props.theme.primary600};
  color: ${(props) => props.theme.background0};
  display: grid;
  grid-template-columns: 1fr 1fr;
  grid-template-rows: auto auto;
  padding: 1.5rem;
  gap: 0.5rem 1rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    display: flex;
    flex-direction: column;
  }

  p {
    grid-column: span 2;
    flex: 1 1 auto;
    color: ionherit;
    font-size: 0.875rem;

    strong {
      display: block;
      font-size: 1.5rem;
      line-height: 1.2;
      margin-bottom: 0.5rem;
    }

    em {
      font-weight: 600;
      font-style: normal;
    }
  }

  ${Button} {
    border-radius: 0;
  }
`;

const DonationAnnouncement = () => {
  return (
    <StyledWrapper>
      <p>
        <strong>La France insoumise a besoin de vous !</strong>
        Vous êtes disponible pour voter le 30 juin et/ou le 7 juillet ?{" "}
        <em>Votez deux fois en prenant une procuration !</em> Si vous ne l’êtes
        pas, <em>trouvez quelqu’un pour voter à votre place.</em>
      </p>
      <p>
        <em>Soutenez financièrement la France insoumise !</em> Seuls vos dons
        permettent de financer ses actions et de garantir leur succès. Ces dons
        sont déductibles des impôts à hauteur de 66%.
      </p>
      <Button
        $block
        link
        route="votingProxyLandingPage"
        color="secondary"
        icon="edit-3"
      >
        Espace procurations
      </Button>
      <Button $block link route="donationLanding" color="danger" icon="heart">
        Faire un don
      </Button>
    </StyledWrapper>
  );
};

export default DonationAnnouncement;
