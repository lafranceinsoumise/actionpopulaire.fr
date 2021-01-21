import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Card from "@agir/front/genericComponents/Card";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledHead = styled.header``;
const StyledBody = styled.div``;
const StyledCard = styled(Card)`
  display: flex;
  flex-flow: column nowrap;
  align-items: stretch;
  justify-content: flex-start;
  padding: 1.5rem;

  @media (max-width: ${style.collapse}px) {
    padding: 1rem;
  }

  ${({ highlight }) =>
    highlight
      ? `
    @media (min-width: ${style.collapse}px) {
      border: none;
      background-color: white;
      background: linear-gradient(0, white 1.5rem, transparent 1.5rem),
        linear-gradient(180deg, white 1.5rem, transparent 1.5rem),
        linear-gradient(90deg, ${highlight} 3px, transparent 3px);
    }
  `
      : ""}

  ${StyledHead} {
    flex: 0 0 auto;
    display: flex;
    flex-flow: row nowrap;
    align-items: center;
    height: 1.5rem;
    margin-bottom: 1rem;

    &:empty {
      display: none;
    }

    h4 {
      font-size: 1rem;
      line-height: 1.5rem;
      font-weight: 600;
      padding: 0;
      margin: 0;
    }

    a {
      margin-left: auto;
      flex: 0 0 1.5rem;
      height: 100%;
      display: flex;
      align-items: center;
      justify-content: center;
      color: ${style.black1000};

      ${RawFeatherIcon} {
        width: 1rem;
        height: 1rem;
      }
    }

    h4 + a {
      @media (min-width: ${style.collapse}px) {
        margin-left: 0;
      }
    }
  }

  ${StyledBody} {
    padding: 0;
    margin: 0;
    flex: 1 1 auto;
    font-size: 0.875rem;
    line-height: 1.6;
    color: ${style.black1000};
    font-weight: 400;
  }
`;

const GroupPageCard = (props) => {
  const { title, editUrl, children, ...rest } = props;

  return (
    <StyledCard {...rest}>
      <StyledHead>
        {title && <h4>{title}</h4>}
        {editUrl && (
          <a href={editUrl}>
            <RawFeatherIcon name="edit-2" />
          </a>
        )}
      </StyledHead>
      <StyledBody>{children}</StyledBody>
    </StyledCard>
  );
};

GroupPageCard.propTypes = {
  children: PropTypes.node,
  title: PropTypes.string,
  editUrl: PropTypes.string,
  highlight: PropTypes.string,
};
export default GroupPageCard;
