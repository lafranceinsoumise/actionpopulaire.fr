import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Card from "@agir/front/genericComponents/Card";
import Button from "@agir/front/genericComponents/Button";

const StyledContent = styled.div``;
const StyledCard = styled(Card)`
  padding-top: 1.5rem;
  padding-bottom: 1.5rem;
  display: flex;
  flex-flow: row nowrap;
  align-items: stretch;
  justify-content: flex-start;

  @media (min-width: ${style.collapse}px) {
    border: none;
    box-shadow: none;

    &::before {
      content: "";
      display: block;
      flex: 0 0 3px;
      background-color: ${style.primary500};
      margin-left: -1.5rem;
      margin-right: 30px;
    }
  }

  ${StyledContent} {
    flex: 1 1 auto;
  }

  ${StyledContent} > * {
    margin-left: 0.5rem;
    margin-right: 0.5rem;
  }

  h4 {
    font-size: 1rem;
    font-weight: 600;
    margin-top: 0;
    margin-bottom: 1rem;
  }

  p {
    font-size: 0.875rem;
    font-weight: 400;
  }

  ${Button} {
    margin-top: 0.5rem;
  }
`;

const GroupFacts = (props) => {
  const { donationLink } = props;

  return donationLink ? (
    <StyledCard>
      <StyledContent>
        <h4>Financez les actions du groupe</h4>
        <p>
          Pour que ce groupe puisse financer ses frais de fonctionnement et
          s’équiper en matériel, vous pouvez contribuer financièrement.
        </p>
        <p>Chaque euro compte.</p>
        <Button href={donationLink} as="a" color="secondary">
          Faire un don
        </Button>
      </StyledContent>
    </StyledCard>
  ) : null;
};

GroupFacts.propTypes = {
  donationLink: PropTypes.string,
};
export default GroupFacts;
