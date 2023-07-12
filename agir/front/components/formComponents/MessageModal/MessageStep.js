import PropTypes from "prop-types";
import React, { useCallback, useRef, Suspense } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";
import { displayShortDate } from "@agir/lib/utils/time";
import { lazy } from "@agir/front/app/utils";
import Spacer from "@agir/front/genericComponents/Spacer";

import Avatar from "@agir/front/genericComponents/Avatar";
import TextField from "@agir/front/formComponents/TextField";
import StaticToast from "@agir/front/genericComponents/StaticToast";

const EmojiPicker = lazy(() =>
  import("@agir/front/formComponents/EmojiPicker"),
);

const StyledLabel = styled.div``;
const StyledMessage = styled.div``;
const StyledCounter = styled.span`
  font-size: 1rem;
  font-weight: 400;
  line-height: 1;
  color: ${({ $invalid }) => ($invalid ? style.redNSP : "inherit")};
  margin-left: auto;

  @media (max-width: ${style.collapse}px) {
    display: inline;
  }
`;
const StyledWrapper = styled.div`
  padding: 1.5rem;

  ${StyledLabel} {
    display: flex;
    align-items: stretch;
    font-size: 1rem;
    margin-bottom: 1rem;

    ${Avatar} {
      flex: 0 0 auto;
      width: 2.5rem;
      height: 2.5rem;
      margin-top: 5px;
      margin-right: 0.5rem;
    }

    span {
      display: inline-flex;
      flex-direction: column;
      justify-content: center;

      strong,
      em {
        display: block;
      }

      strong {
        font-weight: 600;
      }

      em {
        font-style: normal;
      }

      button {
        border: none;
        padding: 0;
        margin: 0;
        text-decoration: none;
        background: inherit;
        cursor: pointer;
        text-align: center;
        -webkit-appearance: none;
        -moz-appearance: none;
        color: ${style.primary500};

        &:focus,
        &:hover {
          border: none;
          outline: none;
          text-decoration: underline;
        }

        &[disabled] {
          &,
          &:hover,
          &:focus {
            opacity: 0.8;
            text-decoration: none;
            cursor: default;
          }
        }

        @media (max-width: ${style.collapse}px) {
          display: block;
        }
      }
    }
  }

  ${StyledMessage} {
    font-size: 1rem;

    header {
      border-bottom: 1px solid ${style.black100};

      input {
        &,
        &:focus,
        &:hover {
          outline: none;
          border: none;
          margin: 0;
          background-color: transparent;
          padding: 1rem 0;
          font-weight: 500;
          font-size: 1.125rem;
        }
      }
    }

    textarea {
      max-height: 12rem;

      @media (max-width: ${style.collapse}px) {
        max-height: none;
      }

      &,
      &:focus,
      &:hover {
        border: none;
        outline: none;
        padding-left: 0;
        padding-right: 0;
        font-size: 1rem;
        margin: 0;
        background-color: transparent;
      }
    }

    footer {
      display: flex;
      flex-flow: row nowrap;
      justify-content: flex-start;
      align-items: center;

      & > * {
        @media (max-width: ${style.collapse}px) {
          display: none;
        }
      }
    }
  }
`;

const MessageStep = (props) => {
  const {
    disabled,
    errors,
    subject,
    text,
    event,
    user,
    onChange,
    onClearEvent,
    maxLength,
    subjectMaxLength,
    groupPk,
    onBoarding,
  } = props;

  const textFieldRef = useRef();
  const textFieldCursorPosition = useRef();

  const isUserGroup = !!user?.groups?.some((group) => group.id === groupPk);

  const handleEmojiSelect = useCallback(
    (emoji) => {
      if (!Array.isArray(textFieldCursorPosition.current)) {
        onChange("text", text + emoji);
        return;
      }
      const [start, end] = textFieldCursorPosition.current;
      const newValue = text.slice(0, start) + emoji + text.slice(end);
      textFieldCursorPosition.current = [
        start + emoji.length,
        start + emoji.length,
      ];
      onChange("text", newValue);
    },
    [onChange, text],
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

  return (
    <StyledWrapper>
      {!!groupPk && (
        <div
          style={{
            padding: "20px",
            backgroundColor: style.primary50,
            marginBottom: "1rem",
            borderRadius: style.borderRadius,
          }}
        >
          {isUserGroup ? (
            <>
              {onBoarding ? (
                <>
                  Les animateur·ices du groupe ont été informé·es de votre
                  arrivée dans le groupe. Envoyez-leur un message pour vous
                  présenter&nbsp;!
                </>
              ) : (
                <>Contactez les animateur·ices du groupe&nbsp;!</>
              )}
              <Spacer size="0.5rem" />
            </>
          ) : (
            <>
              Vous souhaitez rejoindre ce groupe ou bien recevoir des
              informations&nbsp;? Entamez votre discussion ici&nbsp;!&nbsp;
            </>
          )}
          Vous recevrez leur réponse{" "}
          <strong>par notification et sur votre e-mail</strong> (
          <span style={{ color: style.primary500 }}>{user.email}</span>)
        </div>
      )}
      <StyledLabel>
        <Avatar name={user.displayName} image={user.image} />
        <span>
          <strong>{user.displayName}</strong>
          {event && !!event.name && (
            <em>
              {event.id
                ? `À propos de ${event.name}${
                    event.startTime
                      ? " du " + displayShortDate(event.startTime)
                      : ""
                  }`
                : `Aucun événément associé`}
              &ensp;
              <button disabled={disabled} onClick={onClearEvent}>
                Changer
              </button>
            </em>
          )}
        </span>
      </StyledLabel>
      <StyledMessage>
        <header>
          <TextField
            id="messageSubject"
            value={subject}
            onChange={(e) => onChange("subject", e.target.value)}
            autoFocus
            disabled={disabled}
            placeholder="Objet du message"
            maxLength={subjectMaxLength}
            hasCounter={false}
            autoComplete="off"
          />
        </header>
        <TextField
          ref={textFieldRef}
          textArea
          id="messageContent"
          value={text}
          onChange={(e) => onChange("text", e.target.value)}
          disabled={disabled}
          placeholder="Votre message"
          maxLength={maxLength}
          hasCounter={false}
        />
        <footer>
          <Suspense fallback={null}>
            <EmojiPicker
              onOpen={handleEmojiOpen}
              onSelect={handleEmojiSelect}
            />
          </Suspense>
          {typeof maxLength === "number" && text.length >= maxLength / 2 && (
            <StyledCounter $invalid={text.length > maxLength}>
              {text.length}/{maxLength}
            </StyledCounter>
          )}
        </footer>
        {errors?.subject && (
          <StaticToast style={{ marginTop: "1rem" }}>
            {errors.subject}
          </StaticToast>
        )}
        {errors?.text && (
          <StaticToast style={{ marginTop: "1rem" }}>{errors.text}</StaticToast>
        )}
      </StyledMessage>
    </StyledWrapper>
  );
};
MessageStep.propTypes = {
  disabled: PropTypes.bool,
  subject: PropTypes.string,
  text: PropTypes.string,
  event: PropTypes.object,
  user: PropTypes.shape({
    displayName: PropTypes.string.isRequired,
    image: PropTypes.string,
  }).isRequired,
  onChange: PropTypes.func.isRequired,
  onClearEvent: PropTypes.func,
  maxLength: PropTypes.number,
  subjectMaxLength: PropTypes.number,
};
export default MessageStep;
