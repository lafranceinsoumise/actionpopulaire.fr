import PropTypes from "prop-types";
import React, { useState } from "react";
import styled from "styled-components";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import Popin from "@agir/front/genericComponents/Popin";
import BottomSheet from "@agir/front/genericComponents/BottomSheet";

const Trigger = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: auto;
  height: auto;
  color: inherit;
  background-color: transparent;
  border: none;
  cursor: pointer;

  ${RawFeatherIcon} {
    width: ${({ $size }) => $size};
    height: ${({ $size }) => $size};
  }
`;

const StyledInlineMenu = styled.div`
  display: inline-block;
  position: relative;
`;

const MobileInlineMenu = (props) => (
  <StyledInlineMenu>
    <Trigger type="button" onClick={props.onOpen} $size={props.triggerSize}>
      <RawFeatherIcon name={props.triggerIconName} />
    </Trigger>
    <BottomSheet {...props}>{props.children}</BottomSheet>
  </StyledInlineMenu>
);

const DesktopInlineMenu = (props) => (
  <StyledInlineMenu onMouseEnter={props.onOpen} onMouseLeave={props.onDismiss}>
    <Trigger type="button" onClick={props.onOpen} $size={props.triggerSize}>
      <RawFeatherIcon name={props.triggerIconName} />
    </Trigger>
    <Popin {...props}>{props.children}</Popin>
  </StyledInlineMenu>
);

MobileInlineMenu.propTypes = DesktopInlineMenu.propTypes = {
  onOpen: PropTypes.func,
  onDismiss: PropTypes.func,
  children: PropTypes.node,
  triggerIconName: PropTypes.string,
  triggerSize: PropTypes.string,
};

export const InlineMenu = (props) => {
  const { children, triggerIconName, triggerSize } = props;
  const [isOpen, setIsOpen] = useState(false);

  const handleOpen = React.useCallback(() => setIsOpen(true), []);
  const handleDismiss = React.useCallback(() => setIsOpen(false), []);

  return (
    <ResponsiveLayout
      MobileLayout={MobileInlineMenu}
      DesktopLayout={DesktopInlineMenu}
      triggerIconName={triggerIconName}
      triggerSize={triggerSize}
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
  triggerIconName: PropTypes.string,
  triggerSize: PropTypes.string,
};
InlineMenu.defaultProps = {
  triggerIconName: "more-vertical",
  triggerSize: "2.5rem",
};

export default InlineMenu;
