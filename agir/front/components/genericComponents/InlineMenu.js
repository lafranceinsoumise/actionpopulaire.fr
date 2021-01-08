import PropTypes from "prop-types";
import React, { useState } from "react";
import styled from "styled-components";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import Popin from "@agir/front/genericComponents/Popin";
import BottomSheet from "@agir/front/genericComponents/BottomSheet";

const Trigger = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2.5rem;
  height: 2.5rem;
  color: inherit;
  background-color: transparent;
  border: none;
  cursor: pointer;
`;

const StyledInlineMenu = styled.div`
  display: inline-block;
  position: relative;
`;

const MobileInlineMenu = (props) => (
  <StyledInlineMenu>
    <Trigger onClick={props.onOpen}>
      <FeatherIcon name="more-vertical" />
    </Trigger>
    <BottomSheet {...props}>{props.children}</BottomSheet>
  </StyledInlineMenu>
);

const DesktopInlineMenu = (props) => (
  <StyledInlineMenu onMouseEnter={props.onOpen} onMouseLeave={props.onDismiss}>
    <Trigger onClick={props.onOpen}>
      <FeatherIcon name="more-vertical" />
    </Trigger>
    <Popin {...props}>{props.children}</Popin>
  </StyledInlineMenu>
);

MobileInlineMenu.propTypes = DesktopInlineMenu.propTypes = {
  onOpen: PropTypes.func,
  onDismiss: PropTypes.func,
  children: PropTypes.node,
};

export const InlineMenu = (props) => {
  const { children } = props;
  const [isOpen, setIsOpen] = useState(false);

  const handleOpen = React.useCallback(() => setIsOpen(true), []);
  const handleDismiss = React.useCallback(() => setIsOpen(false), []);

  return (
    <ResponsiveLayout
      MobileLayout={MobileInlineMenu}
      DesktopLayout={DesktopInlineMenu}
      isOpen={isOpen}
      onOpen={handleOpen}
      onDismiss={handleDismiss}
    >
      {children}
    </ResponsiveLayout>
  );
};
InlineMenu.propTypes = {
  children: PropTypes.node,
};

export default InlineMenu;
