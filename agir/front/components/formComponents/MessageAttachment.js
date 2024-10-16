import PropTypes from "prop-types";
import React, { useCallback, useMemo, useRef } from "react";
import styled from "styled-components";

import { useMobileApp } from "@agir/front/app/hooks";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const ACCEPTED_CONTENT_TYPES = [
  "application/pdf", // pdf
  "application/msword", // doc
  "application/vnd.openxmlformats-officedocument.wordprocessingml.document", // do
  "application/vnd.oasis.opendocument.text", // odt
  "application/vnd.ms-excel", // xls
  "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", // xlsx
  "application/vnd.oasis.opendocument.spreadsheet", // ods
  "application/vnd.ms-powerpoint", // ppt
  "application/vnd.openxmlformats-officedocument.presentationml.presentation", // pptx
  "application/vnd.oasis.opendocument.presentation", // odp
  "image/png", // png
  "image/jpeg", // jpeg
  "image/jpg", // jpg
  "image/gif", // gif
];

const StyledIconButton = styled.button`
  display: inline-flex;
  align-items: center;
  justify-content: center;
  height: 1.5rem;
  width: 1.5rem;
  border: none;
  padding: 0;
  margin: -1px 0 0;
  text-decoration: none;
  background: inherit;
  cursor: pointer;
  text-align: center;
  -webkit-appearance: none;
  -moz-appearance: none;
  color: ${(props) => props.theme.text1000};

  &:hover,
  &:focus {
    border: none;
    outline: none;
    opacity: 0.6;
  }
`;

const StyledThumbnail = styled.div`
  width: 3.5rem;
  height: 3.5rem;
  position: relative;
  border-radius: ${(props) => props.theme.borderRadius};
  background-color: ${(props) => props.theme.background0};
  border: none;
  padding: 0;
  margin: 0;
  appearance: none;
  -moz-appearance: none;

  &,
  &:hover,
  &:focus {
    color: ${(props) => props.theme.text1000};
    text-decoration: none;
  }

  &:focus  {
    outline: 1px dotted ${(props) => props.theme.text700};
  }

  & > div {
    width: 100%;
    height: 100%;
    display: flex;
    flex-direction: column;
    align-items: stretch;
    border-radius: ${(props) => props.theme.borderRadius};
    box-shadow: ${(props) => props.theme.cardShadow};
    overflow: hidden;

    & > ${RawFeatherIcon} {
      flex: 1 1 auto;
      background-color: ${(props) => props.theme.secondary500};
      display: flex;
      align-items: center;
      justify-content: center;

      & > svg {
        width: 1.5rem;
        height: 1.5rem;
      }
    }

    & > strong {
      flex: 0 0 auto;
      font-weight: 400;
      padding: 2px 4px;
      white-space: nowrap;
      max-width: 100%;
      text-overflow: ellipsis;
      overflow: hidden;
      text-align: center;
      font-size: 0.625rem;
      line-height: 1.5;
    }

    & > img {
      display: block;
      width: 100%;
      height: 100%;
      object-fit: cover;
      object-position: center center;
    }
  }

  & > button {
    position: absolute;
    top: 0;
    right: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    transform: translate(50%, -50%);
    background-color: ${(props) => props.theme.background0};
    border: none;
    border-radius: 100%;
    box-shadow: inherit;
    border: 1px solid ${(props) => props.theme.text200};
    color: ${(props) => props.theme.text500};
    cursor: pointer;
    padding: 0;
    width: 1.25rem;
    height: 1.25rem;

    &:hover,
    &:focus {
      color: ${(props) => props.theme.text700};
    }

    & > ${RawFeatherIcon} {
      & > svg {
        width: 1rem;
        height: 1rem;
      }
    }
  }
`;

const StyledWrapper = styled.div`
  display: grid;
  width: 100%;
  max-width: 21rem;
  height: auto;
  grid-template-columns: auto 1fr auto;
  grid-template-rows: ${(props) => (props.$small ? "2rem" : "3rem")} auto auto;
  grid-template-areas: "icon name delete" "image image image" "image image image";
  align-items: stretch;
  overflow: hidden;
  border-radius: ${(props) => props.theme.borderRadius};
  box-shadow: ${(props) => props.theme.cardShadow};
  font-size: ${(props) => (props.$small ? "0.75rem" : "0.875rem")};
  cursor: ${(props) => (props.onClick ? "pointer" : "default")};

  @media (max-width: ${(props) => props.theme.collapse}px) {
    max-width: 100%;
  }

  & > ${RawFeatherIcon} {
    grid-area: icon;
    background-color: ${(props) => props.theme.secondary500};
    width: ${(props) => (props.$small ? "2rem" : "2.625rem")};
    display: flex;
    align-items: center;
    justify-content: center;

    & > svg {
      width: ${(props) => (props.$small ? "1rem" : "1.5rem")};
      height: ${(props) => (props.$small ? "1rem" : "1.5rem")};
    }
  }

  & > strong {
    align-self: center;
    font-weight: 400;
    padding: 0 ${(props) => (props.$small ? "0.5rem" : "1rem")};
    white-space: nowrap;
    max-width: 100%;
    text-overflow: ellipsis;
    overflow: hidden;
  }

  & > button,
  & > a {
    grid-area: delete;
    display: flex;
    align-items: center;
    justify-content: center;
    width: ${(props) => (props.$small ? "2.5rem" : "3rem")};
    background-color: transparent;
    border: none;
    color: ${(props) => props.theme.text500};
    cursor: pointer;

    &:hover,
    &:focus {
      color: ${(props) => props.theme.text700};
    }

    & > ${RawFeatherIcon} {
      & > svg {
        width: ${(props) => (props.$small ? "1rem" : "1.5rem")};
        height: ${(props) => (props.$small ? "1rem" : "1.5rem")};
      }
    }
  }

  & > img {
    grid-area: image;
    display: block;
    width: 100%;
    height: auto;
    min-height: 5rem;
    max-height: 14rem;
    object-fit: cover;
    object-position: center center;
  }
`;

export const useFileInput = (onChange) => {
  const attachmentInputRef = useRef(null);

  const handleChange = useCallback(
    (e) => {
      const file =
        e?.target?.files && e.target.files[e.target.files.length - 1];

      file &&
        onChange({
          name: file.name,
          file,
        });
    },
    [onChange],
  );

  const handleClear = useCallback(() => {
    onChange(null);
    attachmentInputRef.current.value = null;
  }, [onChange]);

  const handleAttach = useCallback(() => {
    attachmentInputRef.current.click();
  }, []);

  const input = useMemo(
    () => (
      <input
        style={{ display: "none" }}
        type="file"
        ref={attachmentInputRef}
        onChange={handleChange}
        accept={ACCEPTED_CONTENT_TYPES.join(", ")}
      />
    ),
    [handleChange],
  );

  return [handleClear, handleAttach, input];
};

export const IconFileInput = (props) => {
  return (
    <StyledIconButton type="button" {...props}>
      <RawFeatherIcon
        name="paperclip"
        strokeWidth={1.5}
        width="1.5rem"
        height="1.5rem"
      />
    </StyledIconButton>
  );
};

const MessageAttachment = (props) => {
  const {
    file,
    name,
    small = false,
    thumbnail = false,
    onDelete,
    tabIndex,
    ...rest
  } = props;

  const { isMobileApp } = useMobileApp();
  const downloadLinkRef = useRef();

  const isImage = useMemo(
    () => name && name.match(/\.(jpg|jpeg|png|gif)$/i),
    [name],
  );

  const fileURI = useMemo(() => {
    if (!file) {
      return "";
    }

    if (typeof file === "string") {
      return file;
    }

    return URL.createObjectURL(file);
  }, [file]);

  const handleDelete = useCallback(
    (e) => {
      if (!onDelete) {
        return;
      }
      e.stopPropagation();
      e.preventDefault();
      onDelete();
    },
    [onDelete],
  );

  const handleDownload = useCallback((e) => {
    downloadLinkRef.current &&
      e.target !== downloadLinkRef.current &&
      !downloadLinkRef.current.contains(e.target) &&
      downloadLinkRef.current.click();
  }, []);

  if (!file) {
    return null;
  }

  if (thumbnail) {
    return (
      <StyledThumbnail
        {...rest}
        as={onDelete ? undefined : "button"}
        download={onDelete ? undefined : name}
        href={onDelete ? undefined : fileURI}
        tabIndex={tabIndex}
      >
        <div>
          {!isImage && <RawFeatherIcon name="file-text" />}
          {isImage ? <img src={fileURI} alt={name} /> : <strong>{name}</strong>}
        </div>
        {onDelete && (
          <button
            tabIndex={tabIndex}
            aria-label="Supprimer la pièce-jointe"
            onClick={handleDelete}
          >
            <RawFeatherIcon name="x" />
          </button>
        )}
      </StyledThumbnail>
    );
  }

  return (
    <StyledWrapper
      {...rest}
      $small={small && !isImage}
      $image={!isImage}
      onClick={onDelete ? undefined : handleDownload}
    >
      {!isImage && <RawFeatherIcon name="paperclip" />}
      <strong>{name}</strong>
      {onDelete ? (
        <button
          tabIndex={tabIndex}
          aria-label="Supprimer la pièce-jointe"
          onClick={handleDelete}
        >
          <RawFeatherIcon name="trash-2" />
        </button>
      ) : (
        <a
          ref={downloadLinkRef}
          tabIndex={tabIndex}
          aria-label="Télécharger la pièce-jointe"
          download={name}
          href={fileURI}
          target={!isMobileApp ? "_blank" : undefined}
          rel="noreferrer"
        >
          <RawFeatherIcon name="download" />
        </a>
      )}
      {isImage && <img src={fileURI} alt={name} />}
    </StyledWrapper>
  );
};

MessageAttachment.propTypes = {
  file: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
  name: PropTypes.string,
  tabIndex: PropTypes.number,
  small: PropTypes.bool,
  thumbnail: PropTypes.bool,
  onDelete: PropTypes.func,
};

export default MessageAttachment;
