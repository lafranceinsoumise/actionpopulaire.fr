import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import styled from "styled-components";

import BottomSheet from "@agir/front/genericComponents/BottomSheet";
import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Popin from "@agir/front/genericComponents/Popin";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import Spacer from "@agir/front/genericComponents/Spacer";
import StyledMenuList from "./StyledMenuList";

const StyledWrapper = styled.div`
  display: flex;
  width: 100%;
  flex-flow: column nowrap;
  gap: 0.5rem;

  ${Button} {
    ${"" /* TODO: remove after Button refactoring merge */}
    width: 100%;
    margin: 0;
    justify-content: center;
  }
`;

const FollowerActions = ({ onJoin, onQuit }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const openMenu = useCallback(() => setIsMenuOpen(true), []);
  const closeMenu = useCallback(() => setIsMenuOpen(false), []);

  return (
    <StyledWrapper>
      <div style={{ position: "relative" }}>
        <Button $block onClick={openMenu} color="confirmed">
          <RawFeatherIcon name="rss" width="1.5rem" height="1.5rem" />
          <Spacer size="10px" />
          Vous êtes abonné·e
          <Spacer size="10px" />
          <RawFeatherIcon name="chevron-down" widht="1rem" height="1rem" />
        </Button>
        <ResponsiveLayout
          MobileLayout={BottomSheet}
          DesktopLayout={Popin}
          isOpen={isMenuOpen}
          onDismiss={closeMenu}
          position="bottom"
          shouldDismissOnClick
        >
          <StyledMenuList>
            <li>
              <button type="button" onClick={onQuit}>
                <RawFeatherIcon name="x" width="1rem" height="1rem" />
                <Spacer size=".5rem" />
                Arrêter d’être abonné·e
              </button>
            </li>
          </StyledMenuList>
        </ResponsiveLayout>
      </div>
      <Button $block onClick={onJoin}>
        <RawFeatherIcon name="user-plus" width="1.5rem" height="1.5rem" />
        <Spacer size="10px" />
        Rejoindre
      </Button>
    </StyledWrapper>
  );
};

FollowerActions.propTypes = {
  onJoin: PropTypes.func.isRequired,
  onQuit: PropTypes.func.isRequired,
};

export default FollowerActions;
