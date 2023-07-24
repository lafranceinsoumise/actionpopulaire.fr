import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";
import styled from "styled-components";

import AttachmentList from "./AttachmentList";
import NewAttachmentField from "./NewAttachmentField";
import SpendingRequestHelp from "./SpendingRequestHelp";

const StyledError = styled.div``;

const StyledField = styled.div`
  display: flex;
  flex-flow: column nowrap;
  gap: 1rem;

  ${StyledError} {
    display: flex;
    gap: 0.5rem;
    color: ${(props) => props.theme.redNSP};

    &:empty {
      display: none;
    }
  }
`;

const AttachmentField = (props) => {
  const { value, onChange, error } = props;

  const attachments = useMemo(
    () => value.map((item, i) => ({ ...item, id: i })),
    [value]
  );

  const handleAdd = useCallback(
    (attachment) => {
      onChange([...value, attachment]);
    },
    [value, onChange]
  );

  const handleDelete = useCallback(
    (i) => {
      onChange(value.splice(0, i).concat(value.splice(i + 1)));
    },
    [value, onChange]
  );

  return (
    <StyledField>
      <SpendingRequestHelp helpId="documentTypes" />
      <AttachmentList attachments={attachments} onDelete={handleDelete} />
      <NewAttachmentField onChange={handleAdd} />
      <StyledError>{error}</StyledError>
    </StyledField>
  );
};

AttachmentField.propTypes = {
  value: PropTypes.any,
  onChange: PropTypes.func.isRequired,
  error: PropTypes.string,
};

AttachmentField.displayName = "AttachmentField";

export default AttachmentField;
