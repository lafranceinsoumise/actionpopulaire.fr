import PropTypes from "prop-types";
import React, { useCallback, useEffect, useRef, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import AnimatedMoreHorizontal from "@agir/front/genericComponents/AnimatedMoreHorizontal";
import Avatar from "@agir/front/genericComponents/Avatar";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import TextField from "@agir/front/formComponents/TextField";
import EmojiPicker from "@agir/front/formComponents/EmojiPicker";

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
    padding: ${({ $isExpanded }) => ($isExpanded ? "0.75rem" : ".5rem 1rem")};
    transition: background-color 250ms ease-in-out;

    @media (max-width: ${style.collapse}px) {
      position: ${({ $isExpanded }) => ($isExpanded ? "fixed" : "static")};
      bottom: 0;
      left: 0;
      right: 0;
      border: ${({ $isExpanded }) =>
        $isExpanded ? "none" : `1px solid ${style.black100}`};
      border-radius: ${({ $isExpanded }) => ($isExpanded ? "0" : "8")}px;
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

    p {
      flex: 1 1 auto;
      margin: 0;
      padding: 0;
      font-size: inherit;
      line-height: 1.65;
      color: ${style.black500};
      white-space: nowrap;
      text-overflow: ellipsis;
      overflow: hidden;
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

const ChatCommentField = (props) => {
  const { user, initialValue, id, onSend, isLoading, disabled } = props;

  const fieldWrapperRef = useRef(null);

  const [isFocused, setIsFocused] = useState(false);
  const [value, setValue] = useState(initialValue || "");

  const isExpanded = !!value || isFocused;

  const handleFocus = useCallback(() => {
    setIsFocused(true);
  }, []);

  const handleBlur = useCallback((event) => {
    fieldWrapperRef.current &&
      !fieldWrapperRef.current.contains(event.target) &&
      setIsFocused(false);
  }, []);

  useEffect(() => {
    typeof window !== "undefined" &&
      isFocused &&
      !value &&
      document.addEventListener("click", handleBlur);

    return () => {
      document.removeEventListener("click", handleBlur);
    };
  }, [isFocused, value, handleBlur]);

  const handleInputChange = useCallback((e) => {
    setValue(e.target.value);
  }, []);

  const handleEmojiSelect = useCallback((emoji) => {
    setValue((value) => value + emoji);
  }, []);

  const handleSend = useCallback(
    (e) => {
      e.preventDefault();
      onSend(value);
    },
    [onSend, value]
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
                textArea
                id={id}
                value={value}
                onChange={handleInputChange}
                onFocus={handleFocus}
                autoFocus={isFocused}
                label={user.fullName}
                disabled={disabled || isLoading}
                placeholder="Écrire un commentaire"
              />
              <EmojiPicker onSelect={handleEmojiSelect} small />
            </>
          ) : (
            <>
              <p>Écrire un commentaire</p>
              <FeatherIcon name="smile" color={style.black500} />
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
                <FeatherIcon
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
ChatCommentField.propTypes = {
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
export default ChatCommentField;
