import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import SpendingRequestStatus, {
  STATUS_CONFIG,
} from "../common/SpendingRequestStatus";
import Avatar from "@agir/front/genericComponents/Avatar";
import Card from "@agir/front/genericComponents/Card";
import FaIcon from "@agir/front/genericComponents/FaIcon";
import Spacer from "@agir/front/genericComponents/Spacer";
import { timeAgo } from "@agir/lib/utils/time";

const StyledAvatarFaIcon = styled(FaIcon)``;

const StyledHistoryItem = styled.li`
  --lineX: 1.5rem;
  --line: linear-gradient(
    to right,
    transparent 0%,
    transparent calc(var(--lineX) - 0.5px),
    ${(props) => props.theme.black50} calc(var(--lineX) - 0.5px),
    ${(props) => props.theme.black50} calc(var(--lineX) + 0.5px),
    transparent calc(var(--lineX) + 0.5px),
    transparent 100%
  );
  display: flex;
  flex-flow: row nowrap;
  align-items: center;
  gap: 1rem;
  background: var(--line);
  padding-left: calc(var(--lineX) - 1rem);

  &:first-child {
    background: linear-gradient(
        to bottom,
        white 0%,
        white 50%,
        transparent 50%,
        transparent 100%
      ),
      var(--line);
  }

  &:last-child {
    background: linear-gradient(
        to top,
        white 0%,
        white 50%,
        transparent 50%,
        transparent 100%
      ),
      var(--line);
  }

  &:first-child:last-child {
    background: none;
  }

  @media (max-width: ${(props) => props.theme.collapse}px) {
    --lineX: 1rem;
    gap: 1.5rem;
  }

  & > div:first-child {
    flex: 0 0 2rem;
    width: 2rem;
    height: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    color: ${(props) =>
      props.$admin ? props.theme.primary500 : props.theme.black500};
    background-color: ${(props) =>
      props.$admin ? props.theme.primary50 : props.theme.white};
    border: 1px solid
      ${(props) =>
        props.$admin ? props.theme.primary100 : props.theme.black50};
    border-radius: 100%;
  }

  ${Card} {
    flex: 1 1 100%;
    background-color: ${(props) =>
      props.$admin ? "transparent" : props.theme.black25};
    margin-top: 1rem;
    display: flex;
    flex-flow: column nowrap;
    gap: 0.5rem;
    padding: 1rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      margin-top: 0.5rem;
    }

    h6 {
      text-transform: uppercase;
      margin: 0;
      color: ${(props) => props.theme.black500};
      font-weight: 700;
      font-size: 0.75rem;
      line-height: 1.5;
    }

    p {
      display: flex;
      flex-flow: row nowrap;
      align-items: center;
      gap: 0.75rem;
      margin: 0;

      &:empty {
        display: none;
      }

      ${Avatar}, ${StyledAvatarFaIcon} {
        flex: 0 0 auto;
        width: 3rem;
        height: 3rem;
      }

      ${StyledAvatarFaIcon} {
        display: flex;
        align-items: center;
        justify-content: center;
        color: ${(props) => props.theme.primary500};
        background-color: ${(props) => props.theme.primary100};
        border-radius: 100%;
      }

      & > span {
        display: flex;
        flex-flow: column nowrap;
        line-height: 1.5;

        strong {
          font-weight: 600;
          font-size: 0.875rem;
        }
      }
    }

    p + p {
      background-color: ${(props) =>
        props.$admin ? props.theme.black25 : "transparent"};
      font-style: ${(props) => (props.$admin ? "normal" : "italic")};
      padding: ${(props) => (props.$admin ? "0.5rem 0.75rem" : "0")};
      font-size: 0.875rem;
    }
  }

  &:first-child ${Card} {
    margin-top: 0;
  }
`;

const StyledHistory = styled.ul`
  list-style-type: none;
  margin: 0;
  padding: 0;
`;

const StyledWrapper = styled.div`
  display: flex;
  flex-flow: column nowrap;
  align-items: stretch;
  font-size: 0.875rem;

  & > * {
    margin: 0;
  }
`;

const SpendingRequestHistoryItem = (props) => {
  const { modified, title, comment, status, fromStatus } = props;

  const person = useMemo(
    () =>
      typeof props.person === "object"
        ? props.person
        : { displayName: props.person, isAdmin: true },
    [props.person]
  );
  const statusConfig = STATUS_CONFIG[status];
  const icon = person.isAdmin
    ? statusConfig.icon + ":light"
    : fromStatus
    ? "arrow-right:light"
    : statusConfig.icon + ":light";

  return (
    <StyledHistoryItem $admin={!!person.isAdmin}>
      <div title={fromStatus ? "Changement de statut" : statusConfig.label}>
        <FaIcon size="1rem" icon={icon} />
      </div>
      <Card bordered>
        <h6>{title}</h6>
        <p>
          {person.isAdmin ? (
            <StyledAvatarFaIcon
              size="1.5rem"
              icon="money-check-dollar:regular"
            />
          ) : (
            <Avatar {...person} />
          )}
          <span>
            <strong>{person.displayName}</strong>
            <span>{timeAgo(modified, "day")}</span>
          </span>
        </p>
        <p>{comment}</p>
      </Card>
    </StyledHistoryItem>
  );
};

SpendingRequestHistoryItem.propTypes = {
  id: PropTypes.string,
  modified: PropTypes.string,
  person: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
  title: PropTypes.string,
  comment: PropTypes.string,
  diff: PropTypes.arrayOf(PropTypes.string),
  status: PropTypes.string,
  fromStatus: PropTypes.string,
};

const SpendingRequestHistory = (props) => {
  const { status, history } = props;

  const historyEntries = useMemo(
    // Sort by reversed chronological order
    () =>
      Array.isArray(history)
        ? history.sort((a, b) => parseInt(b.id) - parseInt(a.id))
        : [],
    [history]
  );

  return (
    <StyledWrapper>
      {status && (
        <>
          <h4>Statut</h4>
          <Spacer size="0.5rem" />
          <SpendingRequestStatus {...status} />
        </>
      )}
      {status && history && <Spacer size="2rem" />}
      {history && (
        <>
          <h4>Suivi</h4>
          <Spacer size="1rem" />
          <StyledHistory>
            {historyEntries.map((item) => (
              <SpendingRequestHistoryItem key={item.id} {...item} />
            ))}
          </StyledHistory>
        </>
      )}
    </StyledWrapper>
  );
};

SpendingRequestHistory.propTypes = {
  status: PropTypes.shape({
    code: PropTypes.string,
    label: PropTypes.string,
    explanation: PropTypes.string,
  }),
  history: PropTypes.arrayOf(
    PropTypes.shape({
      id: PropTypes.string,
      modified: PropTypes.string,
      person: PropTypes.oneOfType([PropTypes.string, PropTypes.object]),
      title: PropTypes.string,
      comment: PropTypes.string,
      diff: PropTypes.arrayOf(PropTypes.string),
      status: PropTypes.string,
      fromStatus: PropTypes.string,
    })
  ),
};

export default SpendingRequestHistory;
