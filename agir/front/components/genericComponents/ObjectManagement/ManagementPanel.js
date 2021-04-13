import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

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
  main {
    width: 100%;
    margin: 0;
  }

  header {
    margin-bottom: 0.5rem;

    &:empty {
      display: none;
    }
  }
`;

const ManagementPanel = (props) => {
  const { showPanel, children } = props;

  if (!showPanel) return <></>;

  return (
    <StyledContainer>
      <StyledPanel>
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
