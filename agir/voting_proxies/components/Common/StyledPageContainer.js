import React from "react";
import styled, { ThemeProvider } from "styled-components";

import {
  StyledPage,
  StyledIllustration,
  StyledBody,
  StyledMain,
  StyledLogo,
} from "./StyledComponents";

import theme from "@agir/front/genericComponents/themes/2022";

const StyledPageContainer = ({ children }) => (
  <ThemeProvider theme={theme}>
    <StyledPage>
      <StyledIllustration aria-hidden="true" />
      <StyledBody>
        <StyledMain>
          <StyledLogo
            alt="Logo Mélenchon 2022"
            route="melenchon2022"
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
