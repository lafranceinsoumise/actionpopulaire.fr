import PropTypes from "prop-types";
import React, { useState } from "react";
import styled from "styled-components";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import { ResponsiveLayout } from "@agir/front/genericComponents/grid";
import Popin from "@agir/front/genericComponents/Popin";
import BottomSheet from "@agir/front/genericComponents/BottomSheet";

const DefaultTrigger = styled.button`
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

export const InlineMenu = (props) => {
  const {
    children,
    Trigger = DefaultTrigger,
    triggerIconName,
    triggerTextContent,
    triggerSize,
    shouldDismissOnClick,
    style,
    className,
  } = props;
  const [isOpen, setIsOpen] = useState(false);

  const handleOpen = React.useCallback(() => setIsOpen(true), []);
  const handleDismiss = React.useCallback(() => setIsOpen(false), []);

  return (
    <StyledInlineMenu style={style} className={className}>
      <Trigger type="button" onClick={handleOpen} $size={triggerSize}>
        {triggerIconName && <RawFeatherIcon name={triggerIconName} />}
        {triggerTextContent && <span>{triggerTextContent}</span>}
      </Trigger>
      <ResponsiveLayout
        MobileLayout={BottomSheet}
        DesktopLayout={Popin}
        isOpen={isOpen}
        onOpen={handleOpen}
        onDismiss={handleDismiss}
        shouldDismissOnClick={shouldDismissOnClick}
        {...props}
      >
        {children}
      </ResponsiveLayout>
    </StyledInlineMenu>
  );
};
InlineMenu.propTypes = {
  children: PropTypes.node,
  Trigger: PropTypes.elementType,
  triggerIconName: PropTypes.string,
  triggerTextContent: PropTypes.string,
  triggerSize: PropTypes.string,
  shouldDismissOnClick: PropTypes.bool,
  style: PropTypes.object,
  className: PropTypes.string,
  hasCloseButton: PropTypes.bool,
};
InlineMenu.defaultProps = {
  triggerIconName: "more-vertical",
  triggerSize: "2.5rem",
};

export default InlineMenu;
