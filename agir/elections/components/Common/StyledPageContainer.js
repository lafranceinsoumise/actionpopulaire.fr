import React from "react";

import { ThemeProvider } from "styled-components";

import {
  StyledPage,
  StyledIllustration,
  StyledBody,
  StyledMain,
  StyledLogo,
} from "./StyledComponents";

import theme from "@agir/front/genericComponents/themes/nupes";

const StyledPageContainer = ({ children }) => (
  <ThemeProvider theme={theme}>
    <StyledPage>
      <StyledIllustration aria-hidden="true" />
      <StyledBody>
        <StyledMain>
          <StyledLogo
            alt="Logo NUPES"
            route="nupes"
            rel="noopener noreferrer"
            target="_blank"
          />
          {children}
        </StyledMain>
      </StyledBody>
    </StyledPage>
  </ThemeProvider>
);

export default StyledPageContainer;
