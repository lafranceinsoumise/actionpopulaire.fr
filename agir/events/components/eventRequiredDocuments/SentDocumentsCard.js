import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";

import Button from "@agir/front/genericComponents/Button";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Spacer from "@agir/front/genericComponents/Spacer";

const StyledCard = styled.figure`
  width: 100%;
  margin: 0;
  padding: 1rem;
  border-radius: ${(props) => props.theme.borderRadius};
  box-shadow: ${(props) => props.theme.cardShadow};
  text-align: left;

  & > * {
    margin: 0;
  }

  h4 {
    font-weight: 600;
    font-size: 16px;
    line-height: 1.5;
    color: ${(props) => props.theme.primary500};
  }

  ul {
    list-style-type: none;
    padding: 0;
    margin: 0;

    li {
      display: flex;
      align-items: center;
      justify-content: flex-start;

      span {
        font-weight: 500;
        flex: 1 1 auto;
        text-align: left;
        padding: 0 0.625rem;
        white-space: nowrap;
        overflow-x: hidden;
        text-overflow: ellipsis;
      }
    }

    li + li {
      padding-top: 0.5rem;
    }
  }
`;

const SentDocumentsCard = (props) => {
  const { documents } = props;

  if (!Array.isArray(documents) || documents.length === 0) {
    return null;
  }

  return (
    <StyledCard>
      <h4>Documents envoyés</h4>
      <Spacer size="1rem" />
      <ul>
        {documents.map((doc) => (
          <li key={doc.id}>
            <RawFeatherIcon as="i" name="file-text" />
            <span>{doc.name}</span>
            <Button
              small
              link
              href={doc.file}
              target="_blank"
              rel="noopener noreferrer"
              color="primary"
            >
              Voir
            </Button>
          </li>
        ))}
      </ul>
    </StyledCard>
  );
};

SentDocumentsCard.propTypes = {
  documents: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.number.isRequired,
      name: PropTypes.string.isRequired,
      type: PropTypes.string.isRequired,
      file: PropTypes.string.isRequired,
    }),
  ),
};

export default SentDocumentsCard;
