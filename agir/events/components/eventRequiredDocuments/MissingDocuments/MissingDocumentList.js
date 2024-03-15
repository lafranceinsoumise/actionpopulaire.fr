import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { displayShortDate } from "@agir/lib/utils/time";
import { routeConfig } from "@agir/front/app/routes.config";

import Button from "@agir/front/genericComponents/Button";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import Link from "@agir/front/app/Link";

const StyledLink = styled(Link)`
  width: 100%;
  text-align: left;
  width: 100%;
  padding: 1rem 1.5rem;
  margin: 0;
  display: flex;
  flex-flow: column nowrap;
  gap: 0.25rem;

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

  & > ${Button} {
    font-weight: 600;
    margin-top: 10px;
    align-self: flex-start;
    background-color: #fbd8dd;
    border-color: #fbd8dd;

    &:hover {
      background-color: #fbd8dddc;
      border-color: #fbd8dddc;
    }
  }
`;

const StyledList = styled.ul`
  width: 100%;
  list-style-type: none;
  margin: 0;
  padding: 0;
  overflow: hidden;
  border-radius: ${(props) => props.theme.borderRadius};
  box-shadow: ${(props) => props.theme.cardShadow};

  ${StyledLink} {
    border-bottom: 1px solid ${(props) => props.theme.black100};
  }
`;

export const MissingDocumentList = (props) => {
  const { projects } = props;

  if (!Array.isArray(projects) || projects.length === 0) {
    return null;
  }

  return (
    <StyledList>
      {projects.map((project) => {
        const { projectId, event, missingDocumentCount, limitDate } = project;
        return (
          <li key={projectId}>
            <StyledLink
              to={routeConfig.eventRequiredDocuments.getLink({
                eventPk: event.id,
              })}
            >
              <strong>
                <span>{event.name}</span>
                <FeatherIcon name="chevron-right" />
              </strong>
              <span>À compléter avant le {displayShortDate(limitDate)}</span>
              <Button small>
                {missingDocumentCount}{" "}
                {missingDocumentCount > 1
                  ? "informations requises"
                  : "information requise"}
              </Button>
            </StyledLink>
          </li>
        );
      })}
    </StyledList>
  );
};

MissingDocumentList.propTypes = {
  projects: PropTypes.arrayOf(
    PropTypes.shape({
      event: PropTypes.shape({
        id: PropTypes.string.isRequired,
        name: PropTypes.string.isRequired,
        endTime: PropTypes.string.isRequired,
      }),
      projectId: PropTypes.number.isRequired,
      missingDocumentCount: PropTypes.number.isRequired,
      limitDate: PropTypes.string.isRequired,
    }),
  ),
};

export default MissingDocumentList;
