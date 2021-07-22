import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { displayShortDate } from "@agir/lib/utils/time";

import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Toast from "@agir/front/genericComponents/Toast";

const StyledToast = styled(Toast)`
  margin: 0 0 2rem;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    width: calc(100vw - 3rem);
    margin: 0 0 1.5rem 1.5rem;
  }

  & > * {
    width: 100%;
    text-align: left;
    margin: 0;
    display: flex;
    flex-flow: column nowrap;
    gap: 0.25rem;
    background-color: transparent;
    border: none;
    cursor: pointer;

    &,
    &:hover,
    &:focus {
      color: ${(props) => props.theme.black1000};
      text-decoration: none;
      outline: none;
    }

    & > strong {
      margin: 0;
      padding: 0;
      font-size: 1rem;
      line-height: 1.5;
      font-weight: 500;
      display: flex;
      align-items: center;

      & > span:first-child {
        flex: 1 1 auto;
        overflow-x: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
      }
    }

    & > span {
      margin: 0;
      padding: 0;
      font-size: 0.875rem;
      font-weight: 400;
      line-height: 1.6;
      color: ${(props) => props.theme.redNSP};
    }
  }
`;

export const MissingDocumentWarning = (props) => {
  const { missingDocumentCount, limitDate, onClick } = props;

  if (!missingDocumentCount) {
    return null;
  }

  return (
    <StyledToast>
      <button type="button" onClick={onClick}>
        <strong>
          <span>
            {missingDocumentCount}{" "}
            {missingDocumentCount > 1
              ? "informations requises"
              : "information requise"}{" "}
            sur vos événements publics
          </span>
          <FeatherIcon name="chevron-right" />
        </strong>
        <span>À compléter avant le {displayShortDate(limitDate)}</span>
      </button>
    </StyledToast>
  );
};

MissingDocumentWarning.propTypes = {
  missingDocumentCount: PropTypes.number,
  limitDate: PropTypes.string,
  onClick: PropTypes.func.isRequired,
};

export default MissingDocumentWarning;
