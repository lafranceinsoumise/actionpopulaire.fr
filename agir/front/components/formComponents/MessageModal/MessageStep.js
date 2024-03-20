import PropTypes from "prop-types";
import React, { Suspense, useCallback, useMemo, useRef } from "react";
import styled from "styled-components";

import { lazy } from "@agir/front/app/utils";
import Spacer from "@agir/front/genericComponents/Spacer";
import style from "@agir/front/genericComponents/_variables.scss";
import { displayShortDate } from "@agir/lib/utils/time";

import MessageAttachment, {
  IconFileInput,
} from "@agir/front/formComponents/MessageAttachment";
import TextField from "@agir/front/formComponents/TextField";
import Avatar from "@agir/front/genericComponents/Avatar";
import StaticToast from "@agir/front/genericComponents/StaticToast";

const EmojiPicker = lazy(
  () => import("@agir/front/formComponents/EmojiPicker"),
);

const StyledLabel = styled.div``;
const StyledMessage = styled.div``;
const StyledCounter = styled.p`
  font-size: 1rem;
  font-weight: 400;
  line-height: 1;
  color: ${({ $invalid }) => ($invalid ? style.redNSP : "inherit")};
  text-align: right;

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
      gap: 1rem;
      justify-content: flex-start;
      align-items: center;
      margin-top: 2rem;

      & > * {
        @media (max-width: ${style.collapse}px) {
          display: none;
        }
      }
    }
  }
`;

const MessageErrors = ({ errors }) => {
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
    <StaticToast key={key} style={{ marginTop: "0.5rem" }}>
      {Array.isArray(err)
        ? err.map((errorMessage) => (
            <span key={errorMessage}>{errorMessage}</span>
          ))
        : err}
    </StaticToast>
  ));
};

const MessageStep = (props) => {
  const {
    disabled,
    errors,
    subject,
    text,
    event,
    attachment,
    user,
    onChange,
    onClearEvent,
    onAttach,
    onClearAttachment,
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
        {typeof maxLength === "number" && text.length >= maxLength / 2 && (
          <StyledCounter $invalid={text.length > maxLength}>
            {text.length}/{maxLength}
          </StyledCounter>
        )}
        <Spacer size="0.5rem" />
        <MessageAttachment
          file={attachment?.file}
          name={attachment?.name}
          onDelete={onClearAttachment}
        />
        <footer>
          <Suspense fallback={null}>
            <EmojiPicker
              onOpen={handleEmojiOpen}
              onSelect={handleEmojiSelect}
            />
          </Suspense>
          <IconFileInput onClick={onAttach} />
        </footer>
        <MessageErrors errors={errors} />
      </StyledMessage>
    </StyledWrapper>
  );
};
MessageStep.propTypes = {
  disabled: PropTypes.bool,
  subject: PropTypes.string,
  text: PropTypes.string,
  event: PropTypes.object,
  attachment: PropTypes.shape({
    file: PropTypes.string,
    name: PropTypes.string,
  }),
  user: PropTypes.shape({
    displayName: PropTypes.string.isRequired,
    image: PropTypes.string,
    groups: PropTypes.arrayOf(PropTypes.shape),
  }).isRequired,
  onChange: PropTypes.func,
  onClearEvent: PropTypes.func,
  onAttach: PropTypes.func,
  onClearAttachment: PropTypes.func,
  maxLength: PropTypes.number,
  subjectMaxLength: PropTypes.number,
  errors: PropTypes.shape({
    text: PropTypes.oneOfType([PropTypes.string, PropTypes.array]),
    subject: PropTypes.oneOfType([PropTypes.string, PropTypes.array]),
    attachment: PropTypes.oneOfType([PropTypes.string, PropTypes.array]),
  }),
  groupPk: PropTypes.string,
  onBoarding: PropTypes.bool,
};
export default MessageStep;
