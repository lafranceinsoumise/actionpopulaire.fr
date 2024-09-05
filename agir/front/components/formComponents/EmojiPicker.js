import { Picker } from "emoji-mart";
import EMOJI_SET_DATA from "@emoji-mart/data/sets/14/twitter";
import FRENCH_I18N from "@emoji-mart/data/i18n/fr";

import PropTypes from "prop-types";
import React, { useCallback, useEffect, useRef, useState } from "react";
import { animated, useTransition } from "@react-spring/web";
import styled from "styled-components";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import * as style from "@agir/front/genericComponents/_variables-light.scss";

const StyledOverlay = styled.div`
  display: ${({ $isOpen }) => ($isOpen ? "block" : "none")};
  position: fixed;
  top: 0;
  right: 0;
  bottom: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: transparent;
  cursor: pointer;
  z-index: 0;
`;

const StyledTriggerIcon = styled(animated.span)`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: ${({ $size }) => $size || "1.5rem"};
  width: ${({ $size }) => $size || "1.5rem"};
  margin: 0;
  padding: 0;
  position: relative;

  & > * {
    flex: 0 0 auto;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    position: absolute;
    line-height: 1.5;
    transform-origin: center center;
    transition:
      opacity,
      transform 100ms ease-in-out;
  }

  & > :first-child {
    opacity: ${({ $isOpen }) => (!$isOpen ? 1 : 0)};
    transform: ${({ $isOpen }) => (!$isOpen ? "scale(1,1)" : "scale(0.5,0.5)")};
  }

  & > :last-child {
    opacity: ${({ $isOpen }) => ($isOpen ? 1 : 0)};
    transform: ${({ $isOpen }) => ($isOpen ? "scale(1,1)" : "scale(0.5,0.5)")};
  }
`;

const StyledTrigger = styled.button`
  display: inline-block;
  border: none;
  padding: 0;
  margin: 0;
  text-decoration: none;
  background: inherit;
  color: inherit;
  font-size: 0;
  line-height: 0;
  cursor: pointer;
  text-align: center;
  -webkit-appearance: none;
  -moz-appearance: none;

  &:hover,
  &:focus {
    border: none;
    outline: none;
    opacity: 0.6;
  }
`;
const StyledPickerWrapper = styled(animated.div)`
  position: absolute;
  width: 350px;
  ${({ $position }) => {
    switch ($position) {
      case "left":
        return "left: 0;";
      default:
        return "right: 0;";
    }
  }}
  right: 0;
  top: 100%;
  text-align: left;
  z-index: 1;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    position: fixed;
    top: unset;
    bottom: 0;
    left: 0;
    right: 0;
    width: 100%;
    z-index: 1;
    transform: none;
  }
`;

const StyledWrapper = styled.div`
  position: relative;
  display: inline-block;
  line-height: 1;
`;

const slideInTransition = {
  from: { opacity: 0, transform: "translateY(1rem)" },
  enter: { opacity: 1, transform: "translateY(0rem)" },
  leave: { opacity: 0, transform: "translateY(1rem)" },
};

const NimblePicker = (props) => {
  const { onEmojiSelect, onKeyDown, ...rest } = props;
  const ref = useRef();

  // Avoid rerenders but still use the latest event handler functions
  const eventHandlers = useRef(null);
  eventHandlers.current = { onEmojiSelect, onKeyDown };
  const handleEmojiSelect = useCallback((emoji) => {
    eventHandlers.current?.onEmojiSelect(emoji);
  }, []);
  const handleKeyDown = useCallback((emoji) => {
    eventHandlers.current?.onKeyDown(emoji);
  }, []);

  useEffect(() => {
    new Picker({
      ref,
      i18n: FRENCH_I18N,
      data: EMOJI_SET_DATA,
      title: "",
      previewPosition: "none",
      skinTonePosition: "none",
      color: style.primary500,
      autoFocus: true,
      onEmojiSelect: handleEmojiSelect,
      onKeyDown: handleKeyDown,
    });
  }, []);

  return <div {...rest} ref={ref} />;
};

const EmojiPicker = (props) => {
  const { onOpen, onClose, onSelect, format, small } = props;

  const [isOpen, setIsOpen] = useState(false);
  const [position, setPosition] = useState("right");

  const triggerRef = useRef(null);

  const toggleOpen = useCallback(() => {
    setIsOpen((state) => !state);
    onOpen && onOpen();
  }, [onOpen]);

  const handleClose = useCallback(() => {
    setIsOpen(false);
    onClose && onClose();
  }, [onClose]);

  const handleKeyClose = useCallback(
    (e) => {
      e.key === "Escape" && handleClose();
    },
    [handleClose],
  );

  const handleEmojiSelect = useCallback(
    (emoji) => {
      onSelect(emoji[format] || emoji.native);
    },
    [onSelect, format],
  );

  const transition = useTransition(isOpen, slideInTransition);

  useEffect(() => {
    isOpen && document.addEventListener("keydown", handleKeyClose);
    return () => document.removeEventListener("keydown", handleKeyClose);
  }, [isOpen, handleKeyClose]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    const { left, right } =
      (triggerRef.current && triggerRef.current.getBoundingClientRect()) || {};
    if (typeof left !== "number" || typeof right !== "number") {
      return;
    }
    window.innerWidth - right > left
      ? setPosition("left")
      : setPosition("right");
  }, []);

  return (
    <>
      <StyledOverlay onClick={handleClose} $isOpen={isOpen} />
      <StyledWrapper>
        <StyledTrigger ref={triggerRef} type="button" onClick={toggleOpen}>
          <StyledTriggerIcon $isOpen={isOpen} $size={small ? "1rem" : "1.5rem"}>
            <RawFeatherIcon
              name="smile"
              width={small ? "1rem" : "1.5rem"}
              color="text1000"
            />
            <em-emoji id="smile" set="twitter" size={small ? 16 : 24} />
          </StyledTriggerIcon>
        </StyledTrigger>
        {transition(
          (style, item) =>
            item && (
              <StyledPickerWrapper style={style} $position={position}>
                <NimblePicker
                  style={{
                    width: "100%",
                    fontFamily: "inherit",
                    fontSize: "0.875rem",
                    lineHeight: "1.5",
                  }}
                  onEmojiSelect={handleEmojiSelect}
                  onKeyDown={handleKeyClose}
                />
              </StyledPickerWrapper>
            ),
        )}
      </StyledWrapper>
    </>
  );
};
EmojiPicker.propTypes = {
  onSelect: PropTypes.func.isRequired,
  onOpen: PropTypes.func,
  onClose: PropTypes.func,
  format: PropTypes.oneOf(["native", "id", "colons", "unified"]),
  small: PropTypes.bool,
};

EmojiPicker.defaultProps = {
  format: "native",
  small: false,
};

export default EmojiPicker;
