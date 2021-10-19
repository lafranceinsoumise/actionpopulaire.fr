import React, { Suspense } from "react";
import styled from "styled-components";

import { lazy } from "@agir/front/app/utils";
import { useResponsiveMemo } from "@agir/front/genericComponents/grid";

const MobileNavBar = lazy(() => import("./MobileNavBar/MobileNavBar"));
const DesktopNavBar = lazy(() => import("./DesktopNavBar/DesktopNavBar"));

const StyledNav = styled.div`
  position: relative;
  width: 100%;
  height: 72px;
  box-shadow: ${(props) => props.theme.elaborateShadow};

  @media (max-width: ${(props) => props.theme.collapse}px) {
    height: 54px;
  }

  & > * {
    margin: 0 auto;
  }
`;

const NavBar = (props) => {
  const NavBar = useResponsiveMemo(MobileNavBar, DesktopNavBar);
  return (
    <StyledNav>
      <Suspense fallback={null}>
        <NavBar {...props} />
      </Suspense>
    </StyledNav>
  );
};

export default NavBar;
