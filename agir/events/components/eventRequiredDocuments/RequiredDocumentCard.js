import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

import { EVENT_DOCUMENT_TYPES } from "./config";

const StyledCard = styled.div`
  overflow: hidden;
  border-radius: ${(props) => props.theme.borderRadius};
  box-shadow: ${(props) => props.theme.cardShadow};
  font-size: 0.875rem;
  width: 100%;
  padding: 0;
  margin: 0;
  text-align: left;

  @media (min-width: ${(props) => props.theme.collapse}px) {
    max-width: 680px;
    display: flex;
    align-items: stretch;
  }

  &::before {
    display: block;
    content: "";
    height: 108px;
    background-image: url(${(props) => props.$img});
    background-repeat: no-repeat;
    background-position: center center;
    background-size: cover;

    @media (min-width: ${(props) => props.theme.collapse}px) {
      flex: 0 0 152px;
      height: auto;
    }
  }

  & > div {
    padding: 1rem;

    @media (min-width: ${(props) => props.theme.collapse}px) {
      flex: 1 1 auto;
      padding: 1.5rem;
    }

    & > * {
      margin: 0;
    }

    h4 {
      color: ${(props) => props.theme.primary500};
      font-weight: 600;
      font-size: 16px;
      line-height: 1.5;
    }

    p {
      line-height: 1.6;
      color: ${(props) => props.theme.black700};
    }

    ${Button} {
      width: 100%;
      border-radius: ${(props) => props.theme.borderRadius};
      font-weight: 600;
      margin: 1rem 0 0;
      justify-content: center;

      @media (min-width: ${(props) => props.theme.collapse}px) {
        justify-content: flex-start;
        display: inline-flex;
        width: auto;
        margin-right: 1rem;
      }
    }
  }
`;

const RequiredDocumentCard = (props) => {
  const { type, onUpload, onDismiss, ...rest } = props;

  if (!type || !EVENT_DOCUMENT_TYPES[type]) {
    return null;
  }

  const { image, name, description, templateLink } = EVENT_DOCUMENT_TYPES[type];

  return (
    <StyledCard {...rest} $img={image}>
      <div>
        <h4>{name}</h4>
        <Spacer size="0.5rem" />
        <p>{description}</p>
        <Button
          onClick={() => onUpload(type)}
          color={onDismiss ? "primary" : "default"}
        >
          <RawFeatherIcon name="upload" style={{ marginRight: "0.5rem" }} />
          Ajouter un justificatif
        </Button>
        {templateLink && (
          <Button as="a" href="" download={templateLink}>
            <RawFeatherIcon name="file" style={{ marginRight: "0.5rem" }} />
            Modèle vierge
          </Button>
        )}
        <br />
        {onDismiss && (
          <Button small color="link" onClick={() => onDismiss(type)}>
            Non appliquable
          </Button>
        )}
      </div>
    </StyledCard>
  );
};

RequiredDocumentCard.propTypes = {
  type: PropTypes.string.isRequired,
  onUpload: PropTypes.func.isRequired,
  onDismiss: PropTypes.func,
};

export default RequiredDocumentCard;
