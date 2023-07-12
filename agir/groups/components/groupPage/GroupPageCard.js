import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import Card from "@agir/front/genericComponents/Card";
import Link from "@agir/front/app/Link";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledHead = styled.header``;
const StyledBody = styled.div``;
const StyledCard = styled(Card)`
  display: flex;
  flex-flow: column nowrap;
  align-items: stretch;
  justify-content: flex-start;
  padding: 0;
  border: none;
  box-shadow: none;

  && {
    @media (min-width: ${style.collapse}px) {
      background-color: transparent;
      margin-bottom: 1.5rem;

      &:last-child {
        margin-bottom: 0;
      }
    }

    @media (max-width: ${style.collapse}px) {
      padding: 1.5rem 1rem;
      box-shadow:
        rgba(0, 35, 44, 0.5) 0px 0px 1px,
        rgba(0, 35, 44, 0.08) 0px 2px 0px;
    }
  }

  ${({ highlight }) =>
    highlight
      ? `
    @media (min-width: ${style.collapse}px) {
      padding: 1.5rem;
      border: none;
      background-color: white;
      background: linear-gradient(0, white 1.5rem, transparent 1.5rem),
        linear-gradient(180deg, white 1.5rem, transparent 1.5rem),
        linear-gradient(90deg, ${highlight} 3px, transparent 3px);
    }
  `
      : ""}

  ${({ outlined }) =>
    outlined
      ? `
    @media (min-width: ${style.collapse}px) {
      padding: 1.5rem;
      border: 1px solid ${style.black100};
    }
  `
      : ""}

  ${StyledHead} {
    flex: 0 0 auto;
    display: flex;
    flex-flow: row nowrap;
    align-items: center;
    height: 1.5rem;
    margin-bottom: 0.5rem;

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
  const { title, editHref, editLinkTo, children, ...rest } = props;

  return (
    <StyledCard {...rest}>
      <StyledHead>
        {title && <h4>{title}</h4>}
        {editHref && (
          <a href={editHref}>
            <RawFeatherIcon name="edit-2" />
          </a>
        )}
        {editLinkTo && (
          <Link to={editLinkTo}>
            <RawFeatherIcon name="edit-2" />
          </Link>
        )}
      </StyledHead>
      <StyledBody>{children}</StyledBody>
    </StyledCard>
  );
};

GroupPageCard.propTypes = {
  children: PropTypes.node,
  title: PropTypes.string,
  editHref: PropTypes.string,
  editLinkTo: PropTypes.string,
  highlight: PropTypes.string,
  outlined: PropTypes.bool,
};
export default GroupPageCard;
