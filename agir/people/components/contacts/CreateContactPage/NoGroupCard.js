import React from "react";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { InlineSpacer } from "@agir/front/genericComponents/Spacer";

const StyledCard = styled.div`
  padding: 1rem;
  box-shadow: ${(props) => props.theme.cardShadow};
  border-radius: ${(props) => props.theme.borderRadius};

  & > div {
    display: flex;
    align-items: flex-start;

    ${RawFeatherIcon} {
      flex: 0 0 auto;
      margin-right: 1rem;
    }

    p {
      flex: 1 1 auto;
      margin-bottom: 1rem;

      strong {
        font-weight: 600;
      }
    }
  }

  footer {
    line-height: 0;
    margin-left: 2.5rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      margin-left: 0;

      ${Button} {
        @media (max-width: ${(props) => props.theme.collapse}px) {
          display: block;
        }
      }
    }
  }
`;

const NoGroupCard = () => {
  return (
    <StyledCard>
      <div>
        <RawFeatherIcon name="alert-triangle" />
        <p>
          <strong>Vous ne faites partie d’aucun groupe d’action.</strong>{" "}
          Rejoignez ou créez un groupe pour pouvoir abonner les soutiens que
          vous obtenez à votre groupe
        </p>
      </div>
      <footer>
        <Button link route="createGroup" color="primary">
          Créer un groupe
        </Button>
        <InlineSpacer size=".5rem" />
        <Button link route="groups">
          Voir les groupes
        </Button>
      </footer>
    </StyledCard>
  );
};

export default NoGroupCard;
