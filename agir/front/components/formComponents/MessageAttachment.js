import PropTypes from "prop-types";
import React, { useCallback, useMemo } from "react";
import styled from "styled-components";

import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledThumbnail = styled.div`
  position: relative;
  width: 3.5rem;
  height: 3.5rem;
  display: flex;
  flex-direction: column;
  align-items: stretch;
  border-radius: ${(props) => props.theme.borderRadius};
  box-shadow: ${(props) => props.theme.cardShadow};

  &,
  &:hover,
  &:focus {
    color: ${(props) => props.theme.black1000};
    text-decoration: none;
  }

  &:focus  {
    outline: 1px dotted ${(props) => props.theme.black700};
  }

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
    border-radius: inherit;
  }

  & > button {
    position: absolute;
    top: 0;
    right: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    transform: translate(50%, -50%);
    background-color: white;
    border: none;
    border-radius: 100%;
    box-shadow: inherit;
    border: 1px solid ${(props) => props.theme.black200};
    color: ${(props) => props.theme.black500};
    cursor: pointer;

    &:hover,
    &:focus {
      color: ${(props) => props.theme.black700};
    }

    & > ${RawFeatherIcon} {
      height: 1.25rem;
      height: 1.25rem;

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
    color: ${(props) => props.theme.black500};
    cursor: pointer;

    &:hover,
    &:focus {
      color: ${(props) => props.theme.black700};
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
    max-height: 14rem;
    min-height: 5rem;
    object-fit: cover;
    object-position: center center;
  }
`;

const MessageAttachment = (props) => {
  const { file, name, small = false, thumbnail = false, onDelete } = props;
  const isImage = useMemo(
    () => name && name.match(/\.(jpg|jpeg|png|gif)$/i),
    [name],
  );

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

  if (!file) {
    return null;
  }

  if (thumbnail) {
    return (
      <StyledThumbnail as="a" download={name} href={file}>
        {!isImage && <RawFeatherIcon name="file-text" />}
        {isImage ? <img src={file} alt={name} /> : <strong>{name}</strong>}
        {onDelete && (
          <button aria-label="Supprimer la pièce-jointe" onClick={handleDelete}>
            <RawFeatherIcon name="x" />
          </button>
        )}
      </StyledThumbnail>
    );
  }

  return (
    <StyledWrapper $small={small && !isImage} $image={!isImage}>
      {!isImage && <RawFeatherIcon name="paperclip" />}
      <strong>{name}</strong>
      {onDelete ? (
        <button aria-label="Supprimer la pièce-jointe" onClick={handleDelete}>
          <RawFeatherIcon name="trash-2" />
        </button>
      ) : (
        <a aria-label="Télécharger la pièce-jointe" download={name} href={file}>
          <RawFeatherIcon name="download" />
        </a>
      )}
      {isImage && <img src={file} alt={name} />}
    </StyledWrapper>
  );
};

MessageAttachment.propTypes = {
  file: PropTypes.string.isRequired,
  name: PropTypes.string.isRequired,
  small: PropTypes.bool,
  thumbnail: PropTypes.bool,
  onDelete: PropTypes.func,
};

export default MessageAttachment;
