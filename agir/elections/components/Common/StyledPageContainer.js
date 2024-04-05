import PropTypes from "prop-types";
import React from "react";

import ThemeProvider from "@agir/front/theme/ThemeProvider";

import {
  StyledPage,
  StyledIllustration,
  StyledBody,
  StyledMain,
  StyledLogo,
} from "./StyledComponents";

import defaultTheme from "@agir/front/genericComponents/themes/eu24";

const StyledPageContainer = ({ theme = defaultTheme, children }) => (
  <ThemeProvider theme={theme}>
    <StyledPage>
      <StyledIllustration aria-hidden="true" />
      <StyledBody>
        <StyledMain>
          <StyledLogo
            alt="Logo la France insoumise"
            route="lafranceinsoumise"
            rel="noopener noreferrer"
            target="_blank"
          />
          {children}
        </StyledMain>
      </StyledBody>
    </StyledPage>
  </ThemeProvider>
);

StyledPageContainer.propTypes = {
  theme: PropTypes.object,
  children: PropTypes.node,
};

export default StyledPageContainer;
