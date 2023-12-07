import React from "react";
import styled from "styled-components";

import illustration from "./DonationAnnouncementIllustration.svg";
import { Button } from "@agir/donations/common/StyledComponents";

const StyledWrapper = styled.div`
  background-color: #502582;
  color: ${(props) => props.theme.white};
  display: flex;
  align-items: center;
  padding: 1rem 1.5rem;
  gap: 1.5rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    flex-direction: column;
    gap: 0.5rem;
  }

  & > * {
    flex: 0 0 auto;
  }

  p {
    flex: 1 1 auto;
    color: ionherit;
    font-size: 0.875rem;

    strong {
      display: block;
      font-size: 1.125rem;
      line-height: 1.2;
      margin-bottom: 0.25rem;
    }
  }

  ${Button} {
    border-radius: 0;
    max-width: 10rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      align-self: stretch;
      max-width: 100%;
    }
  }
`;

const DonationAnnouncement = () => {
  return (
    <StyledWrapper>
      <img src={illustration} height="80" width="80" />
      <p>
        <strong>La France insoumise a besoin de vos dons</strong>
        Seuls vos dons permettent de financer ses actions et de garantir leur
        succès. Ces dons sont déductibles des impôts à hauteur de 66%.
      </p>
      <Button link route="donationLanding" color="danger">
        FAIRE UN DON
      </Button>
    </StyledWrapper>
  );
};

export default DonationAnnouncement;
