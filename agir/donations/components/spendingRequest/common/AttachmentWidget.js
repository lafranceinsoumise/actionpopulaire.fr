import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";
import styled from "styled-components";

import AttachmentList from "./AttachmentList";
import AttachmentField from "./AttachmentField";
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

const AttachmentWidget = (props) => {
  const { value, onChange, error } = props;

  const attachments = useMemo(() => {
    if (!Array.isArray(value)) {
      return [];
    }
    if (!Array.isArray(error)) {
      return value.map((item, i) => ({ ...item, id: i }));
    }

    return value.map((item, i) => ({ ...item, id: i, error: error[i] }));
  }, [value, error]);

  const handleAdd = useCallback(
    (attachment) => {
      Array.isArray(value)
        ? onChange([...value, attachment])
        : onChange([attachment]);
    },
    [value, onChange],
  );

  const handleDelete = useCallback(
    (i) => {
      Array.isArray(value)
        ? onChange([...value.slice(0, i), ...value.slice(i + 1)], i)
        : onChange([]);
    },
    [value, onChange],
  );

  return (
    <StyledField>
      <SpendingRequestHelp helpId="documentTypes" />
      <AttachmentList attachments={attachments} onDelete={handleDelete} />
      <AttachmentField onChange={handleAdd} />
      <StyledError>{error && !Array.isArray(error) ? error : null}</StyledError>
    </StyledField>
  );
};

AttachmentWidget.propTypes = {
  value: PropTypes.any,
  onChange: PropTypes.func,
  error: PropTypes.string,
};

AttachmentWidget.displayName = "AttachmentWidget";

export default AttachmentWidget;
