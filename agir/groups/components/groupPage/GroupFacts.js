import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { timeAgo } from "@agir/lib/utils/time";

import Card from "@agir/front/genericComponents/Card";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

const StyledCard = styled(Card)`
  padding-top: 1.5rem;
  padding-bottom: 1.5rem;

  & > * {
    margin-left: 0.5rem;
    margin-right: 0.5rem;
  }
  h4 {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 1rem;
  }

  ul {
    display: inline-flex;
    flex-flow: column wrap;
    align-items: flex-start;
    justify-content: flex-start;
    list-style: none;
    padding: 0;
    font-size: 14px;
    font-weight: 400;
    max-height: 78px;

    @media (max-width: 352px) {
      flex-wrap: nowrap;
      max-height: none;
    }
  }

  li {
    display: inline-flex;
    width: 160px;
    align-items: baseline;
    min-height: 26px;

    span + span {
      padding-left: 0.5rem;
    }
  }
`;

const GroupFacts = (props) => {
  const { facts } = props;

  if (!facts || Object.values(facts).filter(Boolean).length === 0) {
    return null;
  }
  const {
    eventCount,
    memberCount,
    isCertified,
    creationDate,
    lastActivityDate,
  } = facts;

  return (
    <StyledCard>
      <h4>À propos</h4>
      <ul>
        {eventCount && (
          <li>
            <FeatherIcon name="calendar" small inline />
            <span>
              {eventCount} événement{eventCount > 1 && "s"}
            </span>
          </li>
        )}
        {memberCount && (
          <li>
            <FeatherIcon name="users" small inline />
            <span>
              {memberCount} membre{memberCount > 1 && "s"}
            </span>
          </li>
        )}
        {isCertified && (
          <li>
            <FeatherIcon name="check-circle" small inline />
            <span>Groupe certifié</span>
          </li>
        )}
        {creationDate && (
          <li>
            <FeatherIcon name="clock" small inline />
            <span>Créé {timeAgo(creationDate)}</span>
          </li>
        )}
        {lastActivityDate && (
          <li>
            <FeatherIcon name="rss" small inline />
            <span>Dernière activité&nbsp;: {timeAgo(lastActivityDate)}</span>
          </li>
        )}
      </ul>
    </StyledCard>
  );
};

GroupFacts.propTypes = {
  facts: PropTypes.shape({
    eventCount: PropTypes.number,
    memberCount: PropTypes.number,
    isCertified: PropTypes.bool,
    creationDate: PropTypes.string,
    lastActivityDate: PropTypes.string,
  }),
};
export default GroupFacts;
