import { Interval } from "luxon";
import PropTypes from "prop-types";
import React, { useMemo, useState } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { ACTIVITY_STATUS } from "@agir/activity/common/helpers";
import { dateFromISOString, displayHumanDate } from "@agir/lib/utils/time";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import { Column, Row } from "@agir/front/genericComponents/grid";
import EventCard from "@agir/front/genericComponents/EventCard";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";

const StyledChildrenWrapper = styled.div`
  margin-bottom: 0;
  color: ${(props) => (props.$isUnread ? style.black1000 : style.black700)};

  strong,
  a {
    font-weight: 600;
    text-decoration: none;
    color: inherit;
  }

  button {
    font-weight: 600;
    padding: 0;
    text-align: left;
    background-color: transparent;
    border: none;
    border-bottom: 1px dotted transparent;
    cursor: pointer;
    color: inherit;

    &:hover,
    &:focus {
      border-bottom: 1px dotted ${style.black500};
    }
  }
`;

const LowMarginCard = styled(Card)`
  @media only screen and (min-width: ${style.collapse}px) {
    padding: 0;
    border: none;
  }

  ${Button} {
    margin: 0.5rem 0 1rem;
    align-self: flex-start;
    width: auto;
    max-width: 100%;
    overflow: hidden;
    text-overflow: ellipsis;

    @media (max-width: ${style.collapse}px) {
      margin-bottom: 0;
    }
  }
`;

const EventCardContainer = styled(PageFadeIn)`
  margin-top: 1rem;

  @media only screen and (min-width: ${style.collapse}px) {
    padding-left: 2.5rem;
    margin-bottom: 1.5rem;
  }

  & ${Card} {
    box-shadow: none;
    border: 1px solid ${style.black100};
  }
`;

const ActivityCardAction = (props) => {
  const { config } = props;

  const action =
    config && typeof config.action === "function" ? config.action(props) : null;

  if (!action) {
    return null;
  }

  if (action.href && props.id) {
    return (
      <Button
        small
        color="primary"
        link
        href={`/activite/${props.id}/lien/`}
        params={{ next: action.href }}
      >
        {action?.label}
      </Button>
    );
  }

  if (typeof action.onClick === "function") {
    return (
      <Button small color="primary" onClick={action.onClick}>
        {action?.label}
      </Button>
    );
  }

  return (
    <Button small color="primary" link route={action?.route} to={action?.to}>
      {action?.label}
    </Button>
  );
};

ActivityCardAction.propTypes = {
  id: PropTypes.number,
  config: PropTypes.shape({
    action: PropTypes.func,
  }),
};

export const GenericCardContainer = (props) => {
  const {
    id,
    status,
    timestamp,
    event,
    children,
    config,
    onClick,
    isLoadingEventCard,
  } = props;

  const [isUnread, setIsUnread] = useState(
    status !== ACTIVITY_STATUS.STATUS_INTERACTED
  );

  const date = useMemo(
    () =>
      displayHumanDate(dateFromISOString(timestamp))
        .split("")
        .map((ch, i) => (i ? ch : ch.toUpperCase()))
        .join(""),
    [timestamp]
  );

  const iconName = useMemo(() => config.icon || "info", [config]);

  const eventSchedule = useMemo(
    () => event && Interval.fromISO(`${event.startTime}/${event.endTime}`),
    [event]
  );

  if (!config) {
    return null;
  }

  const handleClick =
    onClick && isUnread
      ? async () => {
          await onClick(id);
          setIsUnread(false);
        }
      : undefined;

  return (
    <LowMarginCard onClick={handleClick}>
      <Row gutter="8" align="flex-start">
        <Column width="1rem" collapse={0} style={{ paddingTop: "2px" }}>
          <FeatherIcon
            name={iconName}
            color={isUnread ? style.primary500 : style.black500}
          />
        </Column>
        <Column collapse={0} grow style={{ fontSize: "15px" }}>
          <StyledChildrenWrapper $isUnread={isUnread}>
            {children}
          </StyledChildrenWrapper>
          {!config.hideDate && (
            <p
              style={{
                margin: "0.125rem 0 0",
                fontSize: "13px",
                color: style.black500,
                fontWeight: 400,
              }}
            >
              {date}
            </p>
          )}
          <ActivityCardAction {...props} />
        </Column>
      </Row>
      {config.hasEvent ? (
        <EventCardContainer
          ready={!isLoadingEventCard}
          wait={
            <Skeleton
              style={{
                borderRadius: style.borderRadius,
                margin: "1rem 0 0",
                height: 124,
              }}
              boxes={1}
            />
          }
        >
          {event && <EventCard {...event} schedule={eventSchedule} />}
        </EventCardContainer>
      ) : null}
    </LowMarginCard>
  );
};
GenericCardContainer.propTypes = {
  id: PropTypes.number,
  status: PropTypes.oneOf(Object.values(ACTIVITY_STATUS)),
  event: PropTypes.object,
  timestamp: PropTypes.string,
  children: PropTypes.node,
  config: PropTypes.shape({
    icon: PropTypes.string,
    hasEvent: PropTypes.bool,
    action: PropTypes.func,
    hideDate: PropTypes.bool,
  }),
  onClick: PropTypes.func,
  isLoadingEventCard: PropTypes.bool,
};

export default GenericCardContainer;
