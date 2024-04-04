import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer, { InlineSpacer } from "@agir/front/genericComponents/Spacer";

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
    display: ${(props) => (props.$img ? "block" : "none")};
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
    text-align: center;

    @media (min-width: ${(props) => props.theme.collapse}px) {
      flex: 1 1 auto;
      padding: 1.5rem;
      text-align: left;
    }

    & > * {
      margin: 0;
    }

    h4 {
      color: ${(props) => props.theme.primary500};
      font-weight: 600;
      font-size: 16px;
      line-height: 1.5;
      text-align: left;
    }

    p {
      line-height: 1.6;
      color: ${(props) => props.theme.black700};
      text-align: left;
    }
  }
`;

const RequiredDocumentCard = (props) => {
  const { type, onUpload, onDismiss, embedded, downloadOnly, ...rest } = props;

  if (!type || !EVENT_DOCUMENT_TYPES[type]) {
    return null;
  }

  const {
    image,
    name,
    description,
    templateLink,
    templateLinkLabel = "Télécharger le modèle vierge",
  } = EVENT_DOCUMENT_TYPES[type];

  return (
    <StyledCard {...rest} $img={!embedded ? image : undefined}>
      <div>
        <h4>{name}</h4>
        <Spacer size="0.5rem" />
        <p>{description}</p>
        {!downloadOnly || templateLink ? <Spacer size="1rem" /> : null}
        {!downloadOnly ? (
          <>
            <Button
              color={onDismiss ? "primary" : "default"}
              onClick={() => onUpload(type)}
              icon="upload"
              small={embedded}
            >
              Ajouter un justificatif
            </Button>
            {onDismiss && (
              <>
                <InlineSpacer size="1rem" />
                <Button
                  color="secondary"
                  onClick={() => onDismiss(type)}
                  icon="x"
                  small={embedded}
                >
                  Non applicable
                </Button>
              </>
            )}
            <br />
            {templateLink && (
              <>
                <Spacer size="1rem" />
                <a
                  href={templateLink}
                  target="_blank"
                  rel="noopener noreferrer"
                >
                  {templateLinkLabel}
                </a>
              </>
            )}
          </>
        ) : (
          <Button
            link
            color="primary"
            href={templateLink}
            target="_blank"
            rel="noopener noreferrer"
          >
            <RawFeatherIcon name="download" style={{ marginRight: "0.5rem" }} />
            {templateLinkLabel}
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
  embedded: PropTypes.bool,
  downloadOnly: PropTypes.bool,
};

export default RequiredDocumentCard;
