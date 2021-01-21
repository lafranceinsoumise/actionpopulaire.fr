import PropTypes from "prop-types";
import React, { useCallback, useEffect, useRef, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import AnimatedMoreHorizontal from "@agir/front/genericComponents/AnimatedMoreHorizontal";
import Avatar from "@agir/front/genericComponents/Avatar";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import TextField from "@agir/front/formComponents/TextField";
import EmojiPicker from "@agir/front/formComponents/EmojiPicker";

const StyledCommentButton = styled.button`
  @media (max-width: ${style.collapse}px) {
    display: flex;
    width: 100%;
    margin: 0;
    border-radius: 8px;
    border: 1px solid ${style.black100};
    padding: 0.5rem 0.75rem;
    text-decoration: none;
    background-color: ${({ $disabled }) =>
      $disabled ? style.black50 : style.white};
    font-size: 0.875rem;
    line-height: 1.65;
    color: ${style.black500};
    white-space: nowrap;
    text-overflow: ellipsis;
    overflow: hidden;
    cursor: pointer;
    -webkit-appearance: none;
    -moz-appearance: none;

    &:hover,
    &:focus {
      outline: none;
      background-color: ${style.black50};
      transition: background-color 250ms ease-in-out;
    }
  }
`;
const StyledField = styled.div``;
const StyledAction = styled.div``;
const StyledMessage = styled.div``;
const StyledWrapper = styled.form`
  display: flex;
  max-width: 100%;

  ${Avatar} {
    flex: 0 0 auto;
    width: 2rem;
    height: 2rem;
    margin-top: 5px;
    margin-right: 0.5rem;

    @media (max-width: ${style.collapse}px) {
      display: none;
    }
  }

  ${StyledMessage} {
    display: flex;
    flex: 1 1 auto;
    border-radius: 8px;
    background-color: ${({ $disabled }) =>
      $disabled ? style.black50 : "#FFFFFF"};
    border: 1px solid ${style.black100};
    flex-flow: row nowrap;
    padding: ${({ $isExpanded }) =>
      $isExpanded ? "0.75rem" : ".5rem 0.75rem"};
    transition: background-color 250ms ease-in-out;

    @media (max-width: ${style.collapse}px) {
      position: fixed;
      bottom: 0;
      left: 0;
      right: 0;
      z-index: 1;
      border: none;
      box-shadow: ${style.elaborateShadow};
      border-radius: 0;
      max-height: 50vh;
    }

    &:hover {
      ${({ $isExpanded }) =>
        !$isExpanded ? `background-color: ${style.black50};` : ""}
    }
  }

  ${StyledField} {
    flex: 1 1 auto;
    display: flex;
    flex-flow: ${({ $isExpanded }) => ($isExpanded ? "column" : "row")} nowrap;
    align-items: ${({ $isExpanded }) => ($isExpanded ? "flex-start" : "center")}
      nowrap;
    cursor: ${({ $isExpanded, $disabled }) =>
      $disabled || $isExpanded ? "default" : "pointer"};
    font-size: 0.875rem;

    ${StyledCommentButton} {
      flex: 1 1 auto;
      margin: 0;
      padding: 0;
      font-size: inherit;
      line-height: 1.65;
      color: ${style.black500};
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
      border: none;
      text-align: left;
      background-color: transparent;
      cursor: pointer;
    }

    label {
      font-size: inherit;
    }

    textarea {
      &,
      &:focus,
      &:hover {
        border: none;
        outline: none;
        padding-left: 0;
        padding-right: 0;
        font-size: inherit;
        margin: 0;
        background-color: transparent;
      }
    }

    & > :last-child {
      @media (max-width: ${style.collapse}px) {
        visibility: ${({ $isExpanded }) =>
          $isExpanded ? "hidden" : "visible"};
      }
    }

    & > ${RawFeatherIcon} {
      display: none;
      @media (max-width: ${style.collapse}px) {
        display: inline-block;
        opacity: 0.3;
        transform: rotate(45deg);
      }
    }
  }

  ${StyledAction} {
    flex: 0 0 40px;
    text-align: center;

    button {
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
      transform: rotate(45deg);
      transform-origin: center center;

      &:hover,
      &:focus {
        border: none;
        outline: none;
        opacity: 0.6;
      }
    }
  }
`;

export const CommentButton = (props) => {
  const { onClick } = props;
  return onClick ? (
    <StyledCommentButton onClick={onClick}>
      Écrire un commentaire
    </StyledCommentButton>
  ) : null;
};
CommentButton.propTypes = {
  onClick: PropTypes.func,
};

const CommentField = (props) => {
  const { user, initialValue, id, onSend, isLoading, disabled } = props;

  const fieldWrapperRef = useRef();
  const textFieldRef = useRef();
  const textFieldCursorPosition = useRef();

  const [isFocused, setIsFocused] = useState(false);
  const [value, setValue] = useState(initialValue || "");

  const isExpanded = !!value || isFocused;

  const handleFocus = useCallback(() => {
    setIsFocused(true);
  }, []);

  const blurOnClickOutside = useCallback((event) => {
    fieldWrapperRef.current &&
      !fieldWrapperRef.current.contains(event.target) &&
      setIsFocused(false);
  }, []);

  const blurOnFocusOutside = useCallback(() => {
    fieldWrapperRef.current &&
      document.activeElement &&
      !fieldWrapperRef.current.contains(document.activeElement) &&
      setIsFocused(false);
  }, []);

  useEffect(() => {
    if (typeof window !== "undefined") {
      isFocused &&
        !value &&
        document.addEventListener("click", blurOnClickOutside);
      isFocused &&
        !value &&
        document.addEventListener("keyup", blurOnFocusOutside);

      return () => {
        document.removeEventListener("click", blurOnClickOutside);
        document.removeEventListener("keyup", blurOnFocusOutside);
      };
    }
  }, [isFocused, value, blurOnClickOutside, blurOnFocusOutside]);

  const handleInputChange = useCallback((e) => {
    setValue(e.target.value);
  }, []);

  const handleEmojiSelect = useCallback(
    (emoji) => {
      if (!Array.isArray(textFieldCursorPosition.current)) {
        setValue(value + emoji);
        return;
      }
      const [start, end] = textFieldCursorPosition.current;
      const newValue = value.slice(0, start) + emoji + value.slice(end);
      textFieldCursorPosition.current = [
        start + emoji.length,
        start + emoji.length,
      ];
      setValue(newValue);
    },
    [value]
  );

  const handleEmojiOpen = useCallback(() => {
    if (
      textFieldRef.current &&
      typeof textFieldRef.current.selectionStart === "number" &&
      typeof textFieldRef.current.selectionEnd === "number"
    ) {
      textFieldCursorPosition.current = [
        textFieldRef.current.selectionStart,
        textFieldRef.current.selectionEnd,
      ];
    }
  }, []);

  const handleSend = useCallback(
    (e) => {
      e.preventDefault();
      onSend(value);
    },
    [onSend, value]
  );

  const handleInputKeyDown = useCallback(
    (e) => {
      if (value && e.ctrlKey && e.keyCode === 13) {
        onSend(value);
      }
    },
    [value, onSend]
  );

  return (
    <StyledWrapper
      $isExpanded={isExpanded}
      $disabled={disabled || isLoading}
      onSubmit={handleSend}
    >
      <Avatar name={user.fullName} avatar={user.avatar} />
      <StyledMessage>
        <StyledField
          ref={fieldWrapperRef}
          onClick={!disabled ? handleFocus : undefined}
        >
          {isExpanded ? (
            <>
              <TextField
                ref={textFieldRef}
                textArea
                id={id}
                value={value}
                onChange={handleInputChange}
                onFocus={handleFocus}
                onKeyDown={handleInputKeyDown}
                autoFocus={isFocused}
                label={user.fullName}
                disabled={disabled || isLoading}
                placeholder="Écrire un commentaire"
              />
              <EmojiPicker
                onOpen={handleEmojiOpen}
                onSelect={handleEmojiSelect}
                small
              />
            </>
          ) : (
            <>
              <StyledCommentButton onFocus={handleFocus}>
                Écrire un commentaire
              </StyledCommentButton>
              <RawFeatherIcon name="send" color={style.primary500} small />
            </>
          )}
        </StyledField>
        {isExpanded ? (
          <StyledAction>
            {isLoading ? (
              <AnimatedMoreHorizontal />
            ) : (
              <button
                type="submit"
                disabled={!value}
                aria-label="Envoyer le commentaire"
              >
                <RawFeatherIcon
                  name="send"
                  color={value ? style.primary500 : style.black500}
                />
              </button>
            )}
          </StyledAction>
        ) : null}
      </StyledMessage>
    </StyledWrapper>
  );
};
CommentField.propTypes = {
  user: PropTypes.shape({
    fullName: PropTypes.string.isRequired,
    avatar: PropTypes.string,
  }).isRequired,
  initialValue: PropTypes.string,
  id: PropTypes.string,
  onSend: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  disabled: PropTypes.bool,
};
export default CommentField;
