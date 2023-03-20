import PropTypes from "prop-types";
import React, { useState, useCallback } from "react";
import styled from "styled-components";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import Popin from "@agir/front/genericComponents/Popin";
import BottomSheet from "@agir/front/genericComponents/BottomSheet";
import Button from "@agir/front/genericComponents/Button";

const StyledButtonMenu = styled.div`
  position: relative;

  ${Button} {
    width: 100%;
  }
`;

export const ButtonMenu = (props) => {
  const {
    text,
    children,
    shouldDismissOnClick,
    className,
    MobileLayout,
    DesktopLayout,
    ...buttonProps
  } = props;
  const [isOpen, setIsOpen] = useState(false);

  const handleOpen = useCallback(() => setIsOpen(true), []);
  const handleDismiss = useCallback(() => setIsOpen(false), []);

  return (
    <StyledButtonMenu className={className}>
      <Button {...buttonProps} onClick={handleOpen} style={{ margin: 0 }}>
        {text} &nbsp;
        <RawFeatherIcon name="chevron-down" width="1rem" height="1rem" />
      </Button>
      <ResponsiveLayout
        MobileLayout={MobileLayout || BottomSheet}
        DesktopLayout={DesktopLayout || Popin}
        isOpen={isOpen}
        onDismiss={handleDismiss}
        shouldDismissOnClick={shouldDismissOnClick}
        {...props}
      >
        {children}
      </ResponsiveLayout>
    </StyledButtonMenu>
  );
};
ButtonMenu.propTypes = {
  text: PropTypes.node,
  children: PropTypes.node,
  shouldDismissOnClick: PropTypes.bool,
  className: PropTypes.string,
  MobileLayout: PropTypes.elementType,
  DesktopLayout: PropTypes.elementType,
};

export default ButtonMenu;
