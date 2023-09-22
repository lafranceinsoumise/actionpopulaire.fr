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
`;

const FollowerActions = ({ isLoading, onJoin, onEdit, onQuit }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const openMenu = useCallback(() => setIsMenuOpen(true), []);
  const closeMenu = useCallback(() => setIsMenuOpen(false), []);

  return (
    <StyledWrapper>
      <div style={{ position: "relative" }}>
        <Button
          block
          onClick={openMenu}
          color="confirmed"
          icon="chevron-down"
          rightIcon
        >
          Vous êtes abonné·e
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
              <button type="button" onClick={onEdit}>
                <RawFeatherIcon name="lock" width="1rem" height="1rem" />
                Préférences de confidentialité
              </button>
            </li>
            <li>
              <button type="button" onClick={onQuit}>
                <RawFeatherIcon name="x" width="1rem" height="1rem" />
                Arrêter d’être abonné·e
              </button>
            </li>
          </StyledMenuList>
        </ResponsiveLayout>
      </div>
      <Button
        block
        onClick={onJoin}
        loading={isLoading}
        disabled={isLoading}
        icon="plus"
      >
        Rejoindre
      </Button>
    </StyledWrapper>
  );
};

FollowerActions.propTypes = {
  onJoin: PropTypes.func.isRequired,
  onEdit: PropTypes.func.isRequired,
  onQuit: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
};

export default FollowerActions;
