import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledIllustration = styled.div``;
const StyledTitle = styled.h3``;
const StyledSubtitle = styled.p``;
const StyledBackButton = styled.button`
  @media (min-width: ${style.collapse}px) {
    display: none;
  }

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
const StyledContainer = styled.div`
  background-color: rgba(0, 0, 0, 0.5);
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100vh;
  overflow: auto;

  @media (min-width: ${style.collapse}px) {
    width: calc(100vw - 360px);
    min-width: 70%;
    left: 360px;
  }
`;

const StyledPanel = styled.div`
  padding: 2rem;
  height: 100%;
  overflow: auto;
  background-color: ${style.white};

  width: 100%;
  @media (min-width: ${style.collapse}px) {
    width: 600px;
  }

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

  ${StyledTitle} {
    font-size: 1.25rem;
    line-height: 1.5;
    font-weight: 700;
  }

  ${StyledSubtitle} {
    grid-column: span 2;
    font-size: 0.875rem;
    line-height: 1.5;
    font-weight: normal;
  }
`;

const ManagementPanel = (props) => {
  const { onBack, illustration, showPanel, children } = props;

  if (!showPanel) return <></>;

  return (
    <StyledContainer>
      <StyledPanel>
        <StyledBackButton type="button" onClick={onBack}>
          <RawFeatherIcon
            name="arrow-left"
            aria-label="Retour"
            width="1.5rem"
            height="1.5rem"
          />
        </StyledBackButton>
        {illustration && (
          <StyledIllustration
            aria-hidden="true"
            style={{ backgroundImage: `url(${illustration})` }}
          />
        )}
        <main>{children}</main>
      </StyledPanel>
    </StyledContainer>
  );
};

ManagementPanel.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  children: PropTypes.node,
};

export default ManagementPanel;
