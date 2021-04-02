import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledIllustration = styled.div``;
const StyledActions = styled.div``;
const StyledTitle = styled.h3``;
const StyledSubtitle = styled.p``;
const StyledBackButton = styled.button`
  &,
  &:hover,
  &:focus {
    background-color: transparent;
    border: none;
    box-shadow: none;
    padding: 0 0 0.5rem;
    margin: 0;
    text-align: left;
    cursor: pointer;
  }
  &:hover,
  &:focus {
    opacity: 0.75;
  }
`;
const StyledPanel = styled.div`
  padding: 2rem;
  height: 100%;
  overflow: auto;
  background-color: ${style.white};

  header,
  main,
  ${StyledIllustration}, ${StyledTitle}, ${StyledSubtitle} {
    width: 100%;
    margin: 0;
  }

  header {
    margin-bottom: 0.5rem;

    &:empty {
      display: none;
    }
  }

  ${StyledIllustration} {
    height: 10rem;
    background-repeat: no-repeat;
    background-size: contain;
    background-position: top center;
  }

  ${StyledIllustration} + header {
    padding-top: 2.5rem;
  }

  header {
    display: grid;
    grid-template-columns: auto 1fr;
    grid-template-rows: auto auto;
  }

  ${StyledTitle} {
    font-size: 1.25rem;
    line-height: 1.5;
    font-weight: 700;
  }

  ${StyledActions} {
    display: flex;
    flex-flow: row wrap;
    align-items: flex-start;
    justify-content: flex-end;

    button {
      display: flex;
      align-items: center;
      min-height: 1.5rem;
      background-color: transparent;
      border: none;
      color: ${style.primary500};
      font-size: 0.813rem;
      line-height: 1.5;
      white-space: nowrap;
      text-overflow: ellipsis;

      ${RawFeatherIcon} {
        margin-right: 0.5rem;
      }
    }
  }

  ${StyledSubtitle} {
    grid-column: span 2;
    font-size: 0.875rem;
    line-height: 1.5;
    font-weight: normal;
  }
`;

const ManagementPanel = (props) => {
  const { onBack, illustration, title, subtitle, actions, children } = props;

  return (
    <StyledPanel>
      {typeof onBack === "function" ? (
        <StyledBackButton type="button" onClick={onBack}>
          <RawFeatherIcon
            name="arrow-left"
            aria-label="Retour"
            width="1.5rem"
            height="1.5rem"
          />
        </StyledBackButton>
      ) : null}
      {illustration && (
        <StyledIllustration
          aria-hidden="true"
          style={{ backgroundImage: `url(${illustration})` }}
        />
      )}
      <header>
        {title && <StyledTitle>{title}</StyledTitle>}
        {Array.isArray(actions) && actions.length > 0 ? (
          <StyledActions>
            {actions.slice(0, 2).map((action) => (
              <button key={action.label} onClick={action.onClick}>
                {action.icon && (
                  <RawFeatherIcon
                    name={action.icon}
                    width="1rem"
                    height="1rem"
                  />
                )}
                {action.label}
              </button>
            ))}
          </StyledActions>
        ) : null}
        {subtitle && <StyledSubtitle>{subtitle}</StyledSubtitle>}
      </header>
      <main>{children}</main>
    </StyledPanel>
  );
};

ManagementPanel.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  title: PropTypes.node,
  subtitle: PropTypes.node,
  actions: PropTypes.arrayOf(
    PropTypes.shape({
      label: PropTypes.string.isRequired,
      onClick: PropTypes.string.isRequired,
      icon: PropTypes.string,
    })
  ),
  children: PropTypes.node,
};

export default ManagementPanel;
