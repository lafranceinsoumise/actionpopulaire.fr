import PropTypes from "prop-types";
import React, { useCallback, useEffect, useState } from "react";

import styled from "styled-components";

import FileField from "@agir/front/formComponents/FileField";
import RadioListField from "@agir/front/formComponents/RadioListField";
import TextField from "@agir/front/formComponents/TextField";
import Button from "@agir/front/genericComponents/Button";
import Spacer from "@agir/front/genericComponents/Spacer";
import SpendingRequestHelp from "./SpendingRequestHelp";
import {
  DOCUMENT_TYPE_OPTIONS,
  validateSpendingRequestDocument,
} from "./form.config";
import { useIsDesktop } from "@agir/front/genericComponents/grid";

const StyledWrapper = styled.div`
  footer {
    display: flex;
    flex-flow: row wrap;
    justify-content: start;
    align-items: end;
    gap: 0.5rem 1rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      flex-flow: column nowrap;
      align-items: stretch;
    }

    & > * {
      flex: 0 1 auto;
      max-width: 100%;
    }

    & > p {
      flex: 0 0 100%;
      margin: 0 0 -0.5rem;
      color: ${(props) => props.theme.text700};
    }
  }
`;

const AttachmentField = (props) => {
  const {
    initialValue,
    onChange,
    resetOnChange = true,
    error,
    disabled,
    isLoading,
  } = props;
  const [attachment, setAttachment] = useState(initialValue || {});
  const [errors, setErrors] = useState({});

  const isDesktop = useIsDesktop();

  const handleChangeType = useCallback((type) => {
    setErrors((state) => ({ ...state, type: undefined }));
    setAttachment((state) => ({ ...state, type }));
  }, []);
  const handleChangeTitle = useCallback((e) => {
    setErrors((state) => ({ ...state, title: undefined }));
    setAttachment((state) => ({ ...state, title: e.target.value }));
  }, []);
  const handleChangeFile = useCallback((file) => {
    setErrors((state) => ({ ...state, file: undefined }));
    setAttachment((state) => ({ ...state, file }));
  }, []);

  const handleSubmit = useCallback(() => {
    const validationErrors = validateSpendingRequestDocument(attachment);
    if (validationErrors) {
      setErrors(validationErrors);
      return;
    }

    setErrors({});
    onChange(attachment);
    resetOnChange && setAttachment({});
  }, [attachment, onChange, resetOnChange]);

  const handleKeyDown = useCallback(
    (e) => {
      if (!disabled && e.target.type !== "button" && e.keyCode === 13) {
        e.preventDefault();
        handleSubmit();
      }
    },
    [disabled, handleSubmit],
  );

  useEffect(() => {
    if (!error) {
      return;
    }
    error &&
      setErrors((state) => ({
        ...state,
        ...(typeof error === "string" ? { file: error } : error),
      }));
  }, [error]);

  return (
    <StyledWrapper onKeyDown={handleKeyDown}>
      <RadioListField
        id="type"
        label="Type de pièce-jointe"
        options={Object.values(DOCUMENT_TYPE_OPTIONS)}
        onChange={handleChangeType}
        value={attachment.type}
        error={errors.type}
        disabled={disabled}
      />
      <Spacer size="1.5rem" />
      <TextField
        id="title"
        label="Titre de la pièce-jointe"
        onChange={handleChangeTitle}
        value={attachment.title}
        error={errors.title}
        disabled={disabled}
        maxLength={200}
        hasCounter={false}
      />
      <Spacer size="1rem" />
      <SpendingRequestHelp helpId="documentQuality" />
      <Spacer size="1rem" />
      <footer>
        <p>Formats acceptés&nbsp;: PDF, PNG, JPEG</p>
        <FileField
          id="file"
          label=""
          onChange={handleChangeFile}
          value={attachment.file}
          error={errors.file}
          disabled={disabled}
          block={!isDesktop}
        />
        <Button
          onClick={handleSubmit}
          color="secondary"
          icon={attachment.id ? "check" : "plus"}
          disabled={disabled}
          loading={isLoading}
        >
          {attachment.id ? "Enregistrer" : "Ajouter"}
        </Button>
      </footer>
    </StyledWrapper>
  );
};

AttachmentField.propTypes = {
  initialValue: PropTypes.shape({
    id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
    type: PropTypes.string,
    title: PropTypes.string,
    file: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
  }),
  error: PropTypes.shape({
    type: PropTypes.string,
    title: PropTypes.string,
    file: PropTypes.oneOfType([PropTypes.string, PropTypes.array]),
  }),
  onChange: PropTypes.func,
  disabled: PropTypes.bool,
  isLoading: PropTypes.bool,
  resetOnChange: PropTypes.bool,
};

export default AttachmentField;
