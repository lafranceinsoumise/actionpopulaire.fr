import Card from "@agir/front/genericComponents/Card";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import PropTypes from "prop-types";
import React, {
  forwardRef,
  useCallback,
  useMemo,
  useRef,
  useState,
} from "react";
import styled from "styled-components";

import { DOCUMENT_TYPE_OPTIONS } from "./form.config";

const StyledItem = styled(Card).attrs((props) => ({
  ...props,
  bordered: true,
  as: "li",
}))`
  flex: 0 0 auto;
  display: grid;
  grid-template-columns: 1fr;
  grid-template-rows: auto auto;
  align-items: center;
  gap: 0 1rem;
  font-size: 1rem;
  line-height: 1.5;

  & > span,
  & > strong {
    font-weight: 400;
    grid-column: 1/3;
  }

  & > span {
    grid-row: 1/2;
    color: ${(props) => props.theme.black500};
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
  }

  & > strong {
    grid-row: 2/3;
  }

  & > button,
  & > a {
    background-color: transparent;
    border: none;
    text-decoration: none;
    grid-row: 1/3;
    cursor: pointer;
    color: ${(props) => props.theme.black1000};

    &:hover,
    &:focus {
      outline: none;
      color: ${(props) => props.theme.primary500};
    }

    &[disabled],
    &[disabled]:hover,
    &[disabled]:focus {
      cursor: default;
      color: ${(props) => props.theme.black200};
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

const AttachmentItem = (props) => {
  const { id, type, title, file, name, onEdit, onDelete, disabled } = props;

  const handleEdit = useCallback(() => {
    id && onEdit && onEdit(id);
  }, [id, onEdit]);

  const handleDelete = useCallback(() => {
    id && onDelete && onDelete(id);
  }, [id, onDelete]);

  const typeLabel = useMemo(() => DOCUMENT_TYPE_OPTIONS[type]?.label || type);

  return (
    <StyledItem>
      <span title={typeLabel}>{typeLabel}</span>
      <strong title={title}>{title}</strong>
      <button onClick={handleEdit} disabled={disabled}>
        <RawFeatherIcon
          title="Modifier la pièce-jointe"
          name="edit-2"
          width="1.5rem"
          height="1.5rem"
        />
      </button>
      {onDelete && (
        <button onClick={handleDelete} disabled={disabled}>
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

export default AttachmentList;
