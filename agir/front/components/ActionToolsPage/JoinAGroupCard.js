import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { communeNameOfToIn } from "@agir/lib/utils/display";

import Button from "@agir/front/genericComponents/Button";

import illustration from "./images/JoinAGroupCard.jpg";

const StyledCard = styled.div`
  padding: 1rem;
  background-color: ${(props) => props.theme.primary500};
  border-radius: ${(props) => props.theme.borderRadius};
  color: ${(props) => props.theme.background0};
  display: flex;
  flex-flow: column nowrap;
  gap: 1rem;

  img {
    border-radius: 4px;
  }

  h4 {
    color: inherit;
    margin: 0;
    font-weight: 700;
    font-size: 1rem;
    line-height: 1.5;
  }

  ${Button} {
    align-self: flex-start;
    width: auto;
  }
`;

export const JoinAGroupCard = (props) => {
  const { city, commune } = props;
  return (
    <StyledCard>
      <img src={illustration} />
      <h4>
        Créer ou rejoindre un groupe d’action{" "}
        {commune?.nameOf
          ? `${communeNameOfToIn(commune.nameOf)} et alentours`
          : city
            ? `à ${city} et alentours`
            : "près de chez vous"}
      </h4>
      <Button link route="groupMap" color="secondary">
        Voir la carte
      </Button>
    </StyledCard>
  );
};
JoinAGroupCard.propTypes = {
  city: PropTypes.string,
  commune: PropTypes.shape({
    nameOf: PropTypes.string,
  }),
};
export default JoinAGroupCard;
