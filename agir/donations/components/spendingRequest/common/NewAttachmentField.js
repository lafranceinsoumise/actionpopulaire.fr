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

const StyledForm = styled.form`
  footer {
    display: flex;
    justify-content: space-between;
    align-items: end;
    gap: 1rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      flex-flow: column nowrap;
      justify-content: stretch;
      align-items: start;
    }

    ${Button} {
      @media (max-width: ${(props) => props.theme.collapse}px) {
        width: 100%;
      }
    }
  }
`;

const NewAttachmentField = (props) => {
  const { initialValue, onChange, error, disabled } = props;
  const [attachment, setAttachment] = useState(initialValue || {});
  const [errors, setErrors] = useState({});

  const handleChangeType = useCallback((type) => {
    setAttachment((state) => ({ ...state, type }));
  }, []);
  const handleChangeTitle = useCallback((e) => {
    setAttachment((state) => ({ ...state, title: e.target.value }));
  }, []);
  const handleChangeFile = useCallback((file) => {
    setAttachment((state) => ({ ...state, file }));
  }, []);

  const handleSubmit = useCallback(
    (e) => {
      e.preventDefault();
      const validationErrors = validateSpendingRequestDocument(attachment);
      if (validationErrors) {
        setErrors(validationErrors);
        return;
      }
      onChange(attachment);
      setAttachment({});
      setErrors({});
    },
    [attachment, onChange]
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
    <StyledForm onSubmit={handleSubmit}>
      <RadioListField
        id="type"
        label="Type de pièce jointe"
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
      />
      <Spacer size="1rem" />
      <SpendingRequestHelp helpId="documentQuality" />
      <Spacer size="1rem" />
      <footer>
        <FileField
          id="file"
          label=""
          helpText="Formats acceptés : PDF, JPEG, PNG."
          onChange={handleChangeFile}
          value={attachment.file}
          error={errors.file}
          disabled={disabled}
        />
        <Button type="submit" color="primary" disabled={disabled}>
          Ajouter
        </Button>
      </footer>
    </StyledForm>
  );
};

NewAttachmentField.propTypes = {
  initialValue: PropTypes.shape({
    type: PropTypes.string,
    title: PropTypes.string,
    file: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
  }),
  error: PropTypes.shape({
    type: PropTypes.string,
    title: PropTypes.string,
    file: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
  }),
  onChange: PropTypes.func.isRequired,
  disabled: PropTypes.bool,
};

export default NewAttachmentField;
