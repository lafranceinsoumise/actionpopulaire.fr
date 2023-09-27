import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import { CATEGORY_OPTIONS, FALLBACK_CATEGORY } from "./form.config";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const OPTIONS = Object.values(CATEGORY_OPTIONS);

const StyledIcon = styled.span``;
const StyledCategory = styled.span``;

const StyledCard = styled.div`
  display: flex;
  flex-flow: row nowrap;
  align-items: ${(props) => (props.$small ? "start" : "center")};
  margin-bottom: 0;
  padding: ${(props) => (props.$small ? 0 : "0.75rem 1rem;")};
  gap: ${(props) => (props.$small ? "0.5rem" : "1rem;")};
  color: ${(props) => props.theme.black1000};
  font-size: 1rem;
  border: ${(props) =>
    props.$small ? "none" : "1px solid " + props.theme.black100};
  border-radius: ${(props) => (props.$small ? 0 : props.theme.borderRadius)};

  @media (max-width: ${(props) => props.theme.collapse}px) {
    font-size: 0.875rem;
    line-height: 1.714;
  }

  ${StyledIcon} {
    flex: 0 0 ${(props) => (props.$small ? "1.5rem" : "3rem")};
    width: ${(props) => (props.$small ? "1.5rem" : "3rem")};
    height: ${(props) => (props.$small ? "1.5rem" : "3rem")};
    border-radius: 100%;
    padding: 0;
    margin: 0;
    line-height: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: ${(props) => props.theme.secondary500};

    ${RawFeatherIcon} {
      width: ${(props) => (props.$small ? "0.75rem" : "1.5rem")};
      height: ${(props) => (props.$small ? "0.75rem" : "1.5rem")};
    }
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
  const { category, small = false } = props;

  const option = useMemo(
    () =>
      OPTIONS.find((option) => option.value === category) || {
        ...FALLBACK_CATEGORY,
        value: category,
      },
    [category],
  );

  return (
    <StyledCard $small={small}>
      <StyledIcon>
        <RawFeatherIcon width="1.5rem" height="1.5rem" name={option.icon} />
      </StyledIcon>
      <StyledCategory>
        {!small && (
          <>
            <small>Catégorie de dépense</small>
            <br />
          </>
        )}
        {option.label}
      </StyledCategory>
    </StyledCard>
  );
};

CategoryCard.propTypes = {
  category: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
  small: PropTypes.bool,
};

export default CategoryCard;
