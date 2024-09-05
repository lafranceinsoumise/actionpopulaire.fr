import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";
import styled from "styled-components";

import Card from "@agir/front/genericComponents/Card";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import { DOCUMENT_TYPE_OPTIONS } from "./form.config";

const StyledItem = styled(Card).attrs((props) => ({
  ...props,
  bordered: true,
  as: "li",
  type: props.$error ? "error" : "alert_dismissed",
}))`
  flex: 0 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: auto auto;
  align-items: center;
  gap: 0 0.5rem;
  font-size: 0.875rem;
  line-height: 1.5;

  & > span,
  & > strong {
    grid-column: 1/3;
    color: ${(props) => props.theme.text1000};
    font-weight: 400;
  }

  & > span {
    grid-row: 1/2;
    color: ${(props) => props.theme.text500};
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  & > strong {
    grid-row: 2/3;
  }

  & > strong + span:not(${RawFeatherIcon}) {
    grid-row: 3/4;
    font-size: 0.875rem;
    color: ${(props) => props.theme.error500};
    white-space: normal;
    overflow: unset;
    display: flex;
    flex-flow: column nowrap;
    align-items: stretch;

    &:empty {
      display: none;
    }
  }

  & > button,
  & > a {
    background-color: transparent;
    border: none;
    text-decoration: none;
    grid-row: 1/3;
    cursor: pointer;
    color: ${(props) => props.theme.text1000};

    &:hover,
    &:focus {
      outline: none;
      color: ${(props) => props.theme.primary500};
    }

    &[disabled],
    &[disabled]:hover,
    &[disabled]:focus {
      cursor: default;
      color: ${(props) => props.theme.text200};
    }

    ${RawFeatherIcon} {
      width: 1.5rem;

      @media (max-width: ${(props) => props.theme.collapse}px) {
        width: 1rem;
        height: 1rem;
      }
    }
  }
`;

const StyledList = styled.ul`
  list-style: none;
  display: flex;
  flex-flow: column nowrap;
  gap: 1rem;
  padding: 0;
`;

export const AttachmentItem = (props) => {
  const { id, type, title, file, error, onEdit, onDelete, disabled } = props;

  const handleEdit = useCallback(() => {
    id && onEdit && onEdit(id);
  }, [id, onEdit]);

  const handleDelete = useCallback(() => {
    onDelete && onDelete(id);
  }, [id, onDelete]);

  const typeLabel = useMemo(
    () => DOCUMENT_TYPE_OPTIONS[type]?.label || type,
    [type],
  );

  const hasError = useMemo(
    () => error && Object.values(error).filter(Boolean).length > 0,
    [error],
  );

  return (
    <StyledItem $error={hasError}>
      <span title={typeLabel}>{typeLabel}</span>
      <strong title={title}>
        {title}
        {file?.name ? ` (${file.name})` : ""}
      </strong>
      <span>
        {hasError &&
          Object.values(error).map((err) => <span key={err}>{err}</span>)}
      </span>
      {onEdit && (
        <button type="button" onClick={handleEdit} disabled={disabled}>
          <RawFeatherIcon
            title="Modifier la pièce-jointe"
            name="edit-2"
            width="1.5rem"
            height="1.5rem"
          />
        </button>
      )}
      {onDelete && (
        <button type="button" onClick={handleDelete} disabled={disabled}>
          <RawFeatherIcon
            title="Supprimer la pièce-jointe"
            name="trash-2"
            width="1.5rem"
            height="1.5rem"
          />
        </button>
      )}
      {typeof file === "string" && (
        <a
          href={file}
          target="__blank"
          rel="noopener noreferrer"
          disabled={disabled}
        >
          <RawFeatherIcon
            title="Ouvrir la pièce-jointe"
            name="eye"
            width="1.5rem"
            height="1.5rem"
          />
        </a>
      )}
    </StyledItem>
  );
};

AttachmentItem.propTypes = {
  id: PropTypes.oneOfType([PropTypes.string, PropTypes.number]).isRequired,
  type: PropTypes.string,
  title: PropTypes.string,
  file: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
  error: PropTypes.object,
  onEdit: PropTypes.func,
  onDelete: PropTypes.func,
  disabled: PropTypes.bool,
};

const AttachmentList = (props) => {
  const { attachments, onEdit, onDelete, disabled } = props;

  return Array.isArray(attachments) && attachments.length > 0 ? (
    <StyledList>
      {attachments.map((attachment) => (
        <AttachmentItem
          key={attachment.id}
          {...attachment}
          onEdit={onEdit}
          onDelete={onDelete}
          disabled={disabled}
        />
      ))}
    </StyledList>
  ) : null;
};

AttachmentList.propTypes = {
  attachments: PropTypes.arrayOf(PropTypes.object),
  onEdit: PropTypes.func,
  onDelete: PropTypes.func,
  disabled: PropTypes.bool,
};

export default AttachmentList;
