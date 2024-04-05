import PropTypes from "prop-types";
import React, {
  Suspense,
  useCallback,
  useEffect,
  useMemo,
  useRef,
  useState,
} from "react";
import styled from "styled-components";

import * as style from "@agir/front/genericComponents/_variables.scss";

import { lazy } from "@agir/front/app/utils";
import { useResizeObserver } from "@agir/lib/utils/hooks";

import MessageAttachment, {
  IconFileInput,
  useFileInput,
} from "@agir/front/formComponents/MessageAttachment";
import { useIsDesktop } from "@agir/front/genericComponents/grid";
import TextField from "@agir/front/formComponents/TextField";
import AnimatedMoreHorizontal from "@agir/front/genericComponents/AnimatedMoreHorizontal";
import Avatar from "@agir/front/genericComponents/Avatar";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import StaticToast from "@agir/front/genericComponents/StaticToast";

const EmojiPicker = lazy(
  () => import("@agir/front/formComponents/EmojiPicker"),
);

const PLACEHOLDER_MESSAGE = "Écrire une réponse";
const COMMENT_MAX_LENGTH = 1000;

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

const StyledMessage = styled.div``;
const StyledMessageAttachment = styled(MessageAttachment)``;
const StyledTextField = styled(TextField)``;
const StyledError = styled.p``;
const StyledAction = styled.div``;
const StyledWrapper = styled.form`
  display: flex;
  margin-top: auto;
  align-items: start;
  max-width: 100%;
  gap: 0.5rem;

  @media (max-width: ${style.collapse}px) {
    position: fixed;
    width: 100%;
    bottom: 0;
    left: 0;
    right: 0;
    z-index: 1;
    border: none;
    border-radius: 0;
    padding: 0.5rem 1rem;
    gap: 0;
    max-height: 50vh;
    overflow: hidden;
    overflow-y: auto;
    background-color: white;
    box-shadow:
      0px -3px 3px rgba(0, 35, 44, 0.1),
      0px 2px 0px rgba(0, 35, 44, 0.08);
  }

  & > * {
    flex: 0 0 auto;
  }

  ${Avatar} {
    margin-top: 0.25rem;
    width: 2rem;
    height: 2rem;

    @media (max-width: ${style.collapse}px) {
      display: ${(props) => (!props.$expanded ? "inline-block" : "none")};
      margin-right: 0.5rem;
    }
  }

  ${StyledMessage} {
    flex: 1 1 auto;
    border: none;
    border-radius: ${style.borderRadius};
    background-color: ${({ $disabled }) =>
      $disabled ? style.black100 : style.black50};
    transition: background-color 250ms ease-in-out;
    display: grid;
    grid-template-columns: 1fr auto auto;
    align-content: center;
    align-items: start;
    gap: 0 0.5rem;
    padding: ${(props) =>
      props.$expanded ? "0.5rem 0.875rem 0.875rem" : "0.5rem 0.875rem"};
    max-height: ${(props) => (props.$expanded ? "unset" : "2.5rem")};

    &:hover {
      ${({ $expanded }) =>
        !$expanded ? `background-color: ${style.black100};` : ""}

      @media (max-width: ${style.collapse}px) {
        background-color: white;
      }
    }

    @media (max-width: ${style.collapse}px) {
      background-color: transparent;
      padding: ${(props) =>
        props.$expanded ? "0.5rem 0 0.875rem" : "0.5rem 0 0.5rem 0.5rem"};
    }

    ${StyledTextField}, ${StyledError} {
      grid-column: 1 / -1;
      margin: 0;
      gap: 0;
    }

    ${StyledTextField} {
      grid-row: 2 / 3;
    }

    ${StyledMessageAttachment} {
      margin-bottom: 0.5rem;
    }

    ${StyledTextField} textarea {
      background: transparent;
      border: none;
      outline: none;
      resize: none;
      line-height: 1.65;
      padding: 0;

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

    ${StyledError} {
      color: ${(props) => props.theme.redNSP};
      font-size: 0.875rem;
      display: block;
      display: flex;
      margin-top: 0;
      gap: 0.25rem;
      flex-direction: column;

      & > span {
        display: block;
      }
    }

    ${StyledError} + ${StyledError} {
      margin-top: 0.25rem;
    }
  }

  ${StyledAction} {
    margin-top: 0.45rem;

    & > button {
      display: flex;
      align-items: center;
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

const CommentErrors = ({ errors }) => {
  const formattedErrors = useMemo(() => {
    if (!errors) {
      return [];
    }

    let errs = { ...errors };

    if (errors.attachment) {
      errs.attachment = [];
      Object.values(errors.attachment)
        .filter(Boolean)
        .forEach((err) =>
          Array.isArray(err)
            ? err.forEach((e) => errs.attachment.push(e))
            : errs.attachment.push(err),
        );
    }

    errs = Object.entries(errs).filter(
      ([_key, err]) => !!err && err.length > 0,
    );

    if (errs.length === 0) {
      return [];
    }

    return errs;
  }, [errors]);

  return formattedErrors.map(([key, err]) => (
    <StyledError key={key}>
      {Array.isArray(err)
        ? err.map((errorMessage) => (
            <span key={errorMessage}>{errorMessage}</span>
          ))
        : err}
    </StyledError>
  ));
};

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
    errors,
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
  const textFieldRef = useRef();
  const textFieldCursorPosition = useRef();

  const [isFocused, setIsFocused] = useState(false);
  const [text, setText] = useState(initialValue || "");
  const [attachment, setAttachment] = useState(null);
  const [onClearAttachment, onAttach, attachmentInput] =
    useFileInput(setAttachment);

  const isDesktop = useIsDesktop();
  const isEmpty = !text.trim() && !attachment;
  const isExpanded = !isEmpty || isFocused;
  const maySend = !isLoading && !isEmpty && text.trim().length <= 1000;

  const { height } = useResizeObserver(rootElementRef);

  const updateScroll = useCallback(() => {
    const scrollerElement = scrollerRef.current;
    if (!!scrollerElement) {
      scrollerElement.scrollTo(0, scrollerElement.scrollHeight);
    }
  }, [scrollerRef]);

  const handleFocus = useCallback(() => {
    textFieldRef.current.focus();
    setIsFocused(true);
  }, []);

  const handleAttach = useCallback(() => {
    onAttach();
    handleFocus();
  }, [onAttach, handleFocus]);

  const blurOnClickOutside = useCallback((event) => {
    if (!messageRef.current?.contains(event.target)) {
      setIsFocused(false);
    }
  }, []);

  const blurOnFocusOutside = useCallback(() => {
    if (
      document.activeElement &&
      !messageRef.current?.contains(document.activeElement)
    ) {
      setIsFocused(false);
    }
  }, []);

  const handleInputChange = useCallback((e) => {
    setText(e.target.value);
  }, []);

  const handleInputKeyDown = useCallback(
    (e) => {
      if (maySend && e.ctrlKey && e.keyCode === 13) {
        onSend({ text, attachment });
        hasSubmitted.current = true;
      }
    },
    [maySend, text, attachment, onSend],
  );

  const handleEmojiSelect = useCallback(
    (emoji) => {
      if (!Array.isArray(textFieldCursorPosition.current)) {
        setText(text + emoji);
        return;
      }
      const [start, end] = textFieldCursorPosition.current;
      const newValue = text.slice(0, start) + emoji + text.slice(end);
      textFieldCursorPosition.current = [
        start + emoji.length,
        start + emoji.length,
      ];
      setText(newValue);
    },
    [text],
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
        onSend({ text: text, attachment });
        hasSubmitted.current = true;
      }
    },
    [blurOnClickOutside, maySend, onSend, text, attachment],
  );

  useEffect(() => {
    if (typeof window !== "undefined") {
      if (isFocused && isEmpty) {
        document.addEventListener("click", blurOnClickOutside);
        document.addEventListener("keyup", blurOnFocusOutside);
      }

      return () => {
        document.removeEventListener("click", blurOnClickOutside);
        document.removeEventListener("keyup", blurOnFocusOutside);
      };
    }
  }, [isFocused, isEmpty, attachment, blurOnClickOutside, blurOnFocusOutside]);

  useEffect(() => {
    if (!isLoading && hasSubmitted.current && !errors) {
      hasSubmitted.current = false;
      setText("");
      setAttachment(null);
    }
  }, [isLoading, errors]);

  useEffect(() => {
    updateScroll();
  }, [scrollerRef, id, comments, updateScroll]);

  useEffect(() => {
    scrollerRef.current?.scrollTo(0, scrollerRef.current.scrollHeight);
  }, [scrollerRef, isFocused, height, text]);

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
      $expanded={isExpanded}
      $disabled={isLoading}
      onSubmit={handleSend}
      ref={rootElementRef}
    >
      {attachmentInput}
      <Avatar name={user.displayName} image={user.image} />
      <StyledMessage
        ref={messageRef}
        onClick={handleFocus}
        onTouchStart={handleFocus}
      >
        <StyledTextField
          ref={textFieldRef}
          textArea
          id={id}
          value={text}
          onChange={handleInputChange}
          onKeyDown={handleInputKeyDown}
          onFocus={handleFocus}
          autoFocus={isExpanded}
          label=""
          disabled={isLoading}
          placeholder={placeholder || PLACEHOLDER_MESSAGE}
          maxLength={COMMENT_MAX_LENGTH}
          hasCounter={false}
        />
        {isExpanded &&
          (attachment ? (
            <StyledMessageAttachment
              thumbnail
              file={attachment?.file}
              name={attachment?.name}
              onDelete={onClearAttachment}
            />
          ) : (
            <div />
          ))}
        {isExpanded && <IconFileInput onClick={handleAttach} />}
        {isExpanded && isDesktop && (
          <Suspense fallback={null}>
            <EmojiPicker
              onOpen={handleEmojiOpen}
              onSelect={handleEmojiSelect}
            />
          </Suspense>
        )}
        {isExpanded && <CommentErrors errors={errors} />}
      </StyledMessage>
      <StyledAction>
        {isLoading && <AnimatedMoreHorizontal />}
        {!isLoading && (
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
  errors: PropTypes.object,
  onSend: PropTypes.func.isRequired,
  isLoading: PropTypes.bool,
  readonly: PropTypes.bool,
  isLocked: PropTypes.bool,
  placeholder: PropTypes.string,
  scrollerRef: PropTypes.object,
};
export default CommentField;
