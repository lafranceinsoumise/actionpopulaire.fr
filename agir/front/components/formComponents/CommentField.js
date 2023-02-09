import PropTypes from "prop-types";
import React, {
  useCallback,
  useEffect,
  useRef,
  useState,
  Suspense,
} from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { useResizeObserver } from "@agir/lib/utils/hooks";
import { lazy } from "@agir/front/app/utils";

import AnimatedMoreHorizontal from "@agir/front/genericComponents/AnimatedMoreHorizontal";
import Avatar from "@agir/front/genericComponents/Avatar";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import TextField from "@agir/front/formComponents/TextField";
import StaticToast from "@agir/front/genericComponents/StaticToast";

const EmojiPicker = lazy(() =>
  import("@agir/front/formComponents/EmojiPicker")
);

const StyledCommentButton = styled.button`
  @media (max-width: ${style.collapse}px) {
    display: flex;
    width: 100%;
    margin: 0;
    border-radius: ${style.borderRadius};
    border: none;
    padding: 0.5rem 0.75rem;
    text-decoration: none;
    background-color: ${({ $disabled }) =>
      $disabled ? style.black100 : style.black50};
    font-size: 1rem;
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
  margin-top: auto;
  max-width: 100%;

  @media (max-width: ${style.collapse}px) {
    max-height: 50vh;
  }

  & > ${Avatar} {
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
    border-radius: ${style.borderRadius};
    background-color: ${({ $disabled }) =>
      $disabled ? style.black100 : style.black50};
    border: none;
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
      border-radius: 0;
      max-height: 50vh;
      overflow: hidden;
      overflow-y: auto;
      padding: 1rem;
      background-color: white;
      box-shadow: 0px -3px 3px rgba(0, 35, 44, 0.1),
        0px 2px 0px rgba(0, 35, 44, 0.08);
      align-items: ${({ $isExpanded }) =>
        $isExpanded ? "flex-start" : "center"};
    }

    &:hover {
      ${({ $isExpanded }) =>
        !$isExpanded ? `background-color: ${style.black100};` : ""}

      @media (max-width: ${style.collapse}px) {
        background-color: white;
      }
    }

    & > ${Avatar} {
      display: none;

      @media (max-width: ${style.collapse}px) {
        display: ${({ $isExpanded }) => ($isExpanded ? "none" : "block")};
        flex: 0 0 auto;
        width: 2rem;
        height: 2rem;
        margin: 0;
        margin-right: 0.5rem;
      }
    }
  }

  ${StyledField} {
    flex: 1 1 auto;
    display: flex;
    flex-flow: column nowrap;
    align-items: flex-start nowrap;
    cursor: ${({ $isExpanded, $disabled }) =>
      $disabled || $isExpanded ? "default" : "pointer"};
    font-size: 1rem;

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
      ${({ $isExpanded }) =>
        !$isExpanded &&
        `
      flex: 1 1 auto;
      margin: 0;
      padding: 0;
      font-size: inherit;
      line-height: 1.65;
      `}

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

      &[disabled],
      &[disabled]:hover,
      &[disabled]:focus {
        opacity: 1;
        cursor: default;
      }
    }
  }
`;

const PLACEHOLDER_MESSAGE = "Écrire une réponse";

export const CommentButton = (props) => {
  const { onClick } = props;
  return onClick ? (
    <StyledCommentButton onClick={onClick}>
      {PLACEHOLDER_MESSAGE}
    </StyledCommentButton>
  ) : null;
};
CommentButton.propTypes = {
  onClick: PropTypes.func,
};

const CommentField = (props) => {
  const {
    user,
    initialValue,
    id,
    comments,
    onSend,
    isLoading,
    readonly,
    isLocked,
    placeholder,
    scrollerRef,
  } = props;

  const hasSubmitted = useRef(false);

  const rootElementRef = useRef();
  const messageRef = useRef();
  const fieldWrapperRef = useRef();
  const textFieldRef = useRef();
  const textFieldCursorPosition = useRef();

  const [isFocused, setIsFocused] = useState(false);
  const [value, setValue] = useState(initialValue || "");

  const isExpanded = !!value || isFocused;
  const maySend = !isLoading && value && value.trim().length <= 1000;

  const { height } = useResizeObserver(messageRef);

  const updateScroll = useCallback(() => {
    const scrollerElement = scrollerRef.current;
    if (!!scrollerElement) {
      scrollerElement.scrollTo(0, scrollerElement.scrollHeight);
    }
  }, [scrollerRef]);

  const handleFocus = () => {
    setIsFocused(true);
  };

  const blurOnClickOutside = useCallback((event) => {
    if (!fieldWrapperRef.current?.contains(event.target)) {
      setIsFocused(false);
    }
  }, []);

  const blurOnFocusOutside = useCallback(() => {
    if (
      document.activeElement &&
      !fieldWrapperRef.current?.contains(document.activeElement)
    ) {
      setIsFocused(false);
    }
  }, []);

  useEffect(() => {
    if (typeof window !== "undefined") {
      if (isFocused && !value) {
        document.addEventListener("click", blurOnClickOutside);
        document.addEventListener("keyup", blurOnFocusOutside);
      }

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
      typeof textFieldRef.current?.selectionStart === "number" &&
      typeof textFieldRef.current?.selectionEnd === "number"
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
      blurOnClickOutside(e);
      if (maySend) {
        onSend(value);
        hasSubmitted.current = true;
      }
    },
    [blurOnClickOutside, maySend, onSend, value]
  );

  useEffect(() => {
    if (!isLoading && hasSubmitted.current) {
      hasSubmitted.current = false;
      setValue("");
    }
  }, [isLoading]);

  const handleInputKeyDown = useCallback(
    (e) => {
      if (maySend && e.ctrlKey && e.keyCode === 13) {
        onSend(value);
        hasSubmitted.current = true;
      }
    },
    [maySend, value, onSend]
  );

  useEffect(() => {
    updateScroll();
  }, [scrollerRef, id, comments, updateScroll]);

  useEffect(() => {
    scrollerRef.current?.scrollTo(0, scrollerRef.current.scrollHeight);
  }, [scrollerRef, isFocused, height, value]);

  if (readonly) {
    return null;
  }

  if (isLocked) {
    return (
      <StaticToast $color="grey" style={{ marginTop: 0 }}>
        Cette conversation est close. Vous ne pouvez pas y écrire de réponse.
      </StaticToast>
    );
  }

  return (
    <StyledWrapper
      $isExpanded={isExpanded}
      $disabled={isLoading}
      onSubmit={handleSend}
      ref={rootElementRef}
    >
      <Avatar name={user.displayName} image={user.image} />
      <StyledMessage ref={messageRef}>
        <Avatar name={user.displayName} image={user.image} />
        <StyledField
          ref={fieldWrapperRef}
          onClick={handleFocus}
          onTouchStart={handleFocus}
        >
          <Suspense fallback={null}>
            <TextField
              ref={textFieldRef}
              textArea
              id={id}
              value={value}
              onChange={handleInputChange}
              onKeyDown={handleInputKeyDown}
              autoFocus={isFocused}
              label={isFocused && user.displayName}
              disabled={isLoading}
              placeholder={placeholder || PLACEHOLDER_MESSAGE}
              maxLength={1000}
              hasCounter={false}
            />
            {isFocused && (
              <EmojiPicker
                onOpen={handleEmojiOpen}
                onSelect={handleEmojiSelect}
                small
              />
            )}
          </Suspense>
        </StyledField>
        {isFocused ? (
          <StyledAction>
            {isLoading ? (
              <AnimatedMoreHorizontal />
            ) : (
              <button
                type="submit"
                disabled={!maySend}
                aria-label="Envoyer le commentaire"
              >
                <RawFeatherIcon
                  name="send"
                  color={maySend ? style.primary500 : style.black500}
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
    displayName: PropTypes.string.isRequired,
    image: PropTypes.string,
  }).isRequired,
  initialValue: PropTypes.string,
  id: PropTypes.string,
  comments: PropTypes.array,
  onSend: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  readonly: PropTypes.bool,
  isLocked: PropTypes.bool,
  placeholder: PropTypes.string,
  scrollerRef: PropTypes.object,
};
export default CommentField;
