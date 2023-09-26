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
  position: relative;
`;

const MemberActions = ({ onQuit, onEdit }) => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const openMenu = useCallback(() => setIsMenuOpen(true), []);
  const closeMenu = useCallback(() => setIsMenuOpen(false), []);

  return (
    <StyledWrapper>
      <Button
        $block
        onClick={openMenu}
        color="primary"
        icon="chevron-down"
        rightIcon
      >
        Vous êtes membre
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
              Quitter le groupe
            </button>
          </li>
        </StyledMenuList>
      </ResponsiveLayout>
    </StyledWrapper>
  );
};

MemberActions.propTypes = {
  onEdit: PropTypes.func.isRequired,
  onQuit: PropTypes.func.isRequired,
};

export default MemberActions;
