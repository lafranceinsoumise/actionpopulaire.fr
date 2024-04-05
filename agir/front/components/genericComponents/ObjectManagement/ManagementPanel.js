import PropTypes from "prop-types";
import React, { useEffect } from "react";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";
import { useIsDesktop } from "@agir/front/genericComponents/grid";

const StyledContainer = styled.div`
  background-color: rgba(0, 0, 0, 0.5);
  width: 100%;
  height: 100%;
  isolation: isolate;

  @media (min-width: ${style.collapse}px) {
    display: inline-block;
    width: 600px;
  }
`;

const StyledPanel = styled.div`
  background-color: ${style.white};
  width: 100%;
  height: 100vh;
  padding: 2rem;
  overflow: auto;

  @media (min-width: ${style.collapse}px) {
    width: 600px;
    overflow: auto;
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
  main {
    padding-bottom: 2rem;
  }
`;

const ManagementPanel = ({ children }) => {
  const isDesktop = useIsDesktop();

  // Remove mutliple scroll overlay on mobile
  useEffect(() => {
    const managementMenu = document.querySelector("#managementMenu");
    if (!isDesktop) {
      managementMenu.style.overflow = "hidden";
    }
    return () => (managementMenu.style.overflow = "auto");
  }, []);

  return (
    <StyledContainer>
      <StyledPanel>
        <main>{children}</main>
      </StyledPanel>
    </StyledContainer>
  );
};

ManagementPanel.propTypes = {
  children: PropTypes.node,
};

export default ManagementPanel;
