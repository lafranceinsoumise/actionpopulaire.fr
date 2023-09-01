import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import { CATEGORY_OPTIONS } from "./form.config";

import Card from "@agir/front/genericComponents/Card";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const OPTIONS = Object.values(CATEGORY_OPTIONS);

const StyledIcon = styled.span``;
const StyledCategory = styled.span``;

const StyledCard = styled(Card)`
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
  margin-bottom: 0;
  padding: 0.75rem 1rem;
  gap: 1rem;
  color: ${(props) => props.theme.black1000};
  font-size: 1rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    font-size: 0.875rem;
  }

  ${StyledIcon} {
    flex: 0 0 3rem;
    width: 3rem;
    height: 3rem;
    border-radius: 100%;
    padding: 0;
    margin: 0;
    line-height: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: ${(props) => props.theme.secondary500};
  }

  ${StyledCategory} {
    flex: 1 1 auto;
    font-weight: 400;

    small {
      font-size: inherit;
      line-height: inherit;
      color: ${(props) => props.theme.black500};
    }
  }
`;

const CategoryCard = (props) => {
  const { category } = props;

  const option = useMemo(
    () => OPTIONS.find((option) => option.value === category),
    [category]
  );

  return (
    <StyledCard bordered>
      <StyledIcon>
        <RawFeatherIcon width="1.5rem" height="1.5rem" name={option.icon} />
      </StyledIcon>
      <StyledCategory>
        <small>Catégorie de dépense</small>
        <br />
        {option.label}
      </StyledCategory>
    </StyledCard>
  );
};

CategoryCard.propTypes = {
  category: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
};

export default CategoryCard;
