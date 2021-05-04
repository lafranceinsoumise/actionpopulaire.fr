import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

const StyledContainer = styled.div`
  background-color: rgba(0, 0, 0, 0.5);
  width: 100%;
  height: 100%;

  @media (min-width: ${style.collapse}px) {
    display: inline-block;
    width: 600px;
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
  @media (max-width: ${style.collapse}px) {
    padding: 1.5rem;
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

const ManagementPanel = ({ children }) => (
  <StyledContainer>
    <StyledPanel>
      <main>{children}</main>
    </StyledPanel>
  </StyledContainer>
);

ManagementPanel.propTypes = {
  children: PropTypes.node,
};

export default ManagementPanel;
