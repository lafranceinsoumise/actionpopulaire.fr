import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import { timeAgo } from "@agir/lib/utils/time";

import Card from "./GroupPageCard";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

const StyledList = styled.ul`
  display: inline-flex;
  flex-flow: column wrap;
  list-style: none;
  padding: 0;
  font-size: 14px;
  font-weight: 400;
  columns: 160px 2;

  @media (max-width: 360px) {
    display: block;
  }

  li {
    display: flex;
    width: 160px;
    align-items: baseline;
    min-height: 26px;

    &:nth-child(3) {
      break-after: always;
    }

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
    <Card title="À propos">
      <StyledList>
        {!!eventCount && (
          <li>
            <FeatherIcon name="calendar" small inline />
            <span>
              {eventCount} événement{eventCount > 1 && "s"}
            </span>
          </li>
        )}
        {!!memberCount && (
          <li>
            <FeatherIcon name="users" small inline />
            <span>
              {memberCount} membre{memberCount > 1 && "s"}
            </span>
          </li>
        )}
        {!!isCertified && (
          <li>
            <FeatherIcon name="check-circle" small inline />
            <span>Groupe certifié</span>
          </li>
        )}
        {!!creationDate && (
          <li>
            <FeatherIcon name="clock" small inline />
            <span>Créé {timeAgo(creationDate)}</span>
          </li>
        )}
        {!!lastActivityDate && (
          <li>
            <FeatherIcon name="rss" small inline />
            <span>Dernière activité&nbsp;: {timeAgo(lastActivityDate)}</span>
          </li>
        )}
      </StyledList>
    </Card>
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
