import { Interval } from "luxon";
import PropTypes from "prop-types";
import React, { useMemo } from "react";
import styled from "styled-components";

import style from "@agir/front/genericComponents/_variables.scss";

import { ACTIVITY_STATUS } from "@agir/activity/common/helpers";
import { dateFromISOString, displayHumanDate } from "@agir/lib/utils/time";

import Button from "@agir/front/genericComponents/Button";
import Card from "@agir/front/genericComponents/Card";
import { Column, Row } from "@agir/front/genericComponents/grid";
import EventCard from "@agir/front/genericComponents/EventCard";
import FeatherIcon from "@agir/front/genericComponents/FeatherIcon";

const StyledChildrenWrapper = styled.div`
  margin-bottom: 0;
  color: ${(props) => (props.$isUnread ? style.black1000 : style.black700)};

  strong,
  a {
    font-weight: 600;
    text-decoration: none;
    color: inherit;
  }
`;

const LowMarginCard = styled(Card)`
  @media only screen and (min-width: ${style.collapse}px) {
    padding: 0;
    border: none;
  }

  ${Button} {
    margin: 0.5rem 0 1rem;
    justify-content: center;
    align-self: flex-start;
    width: auto;
    max-width: 100;
    overflow: hidden;
    text-overflow: ellipsis;

    @media (max-width: ${style.collapse}px) {
      margin-bottom: 0;
    }
  }
`;

const EventCardContainer = styled.div`
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

export const GenericCardContainer = React.memo((props) => {
  const { status, timestamp, event, children, config } = props;

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

  const action = useMemo(
    () =>
      config && typeof config.action === "function"
        ? config.action(props)
        : null,
    [props, config]
  );

  if (!config) {
    return null;
  }

  const isUnread = status !== ACTIVITY_STATUS.STATUS_INTERACTED;

  return (
    <LowMarginCard>
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
          {action && (
            <Button
              small
              color="primary"
              as={typeof action.onClick !== "function" ? "Link" : undefined}
              onClick={
                typeof action.onClick === "function" ? action : undefined
              }
              href={action?.href}
              route={action?.route}
              to={action?.to}
            >
              {action?.label}
            </Button>
          )}
        </Column>
      </Row>
      {config.hasEvent && (
        <EventCardContainer>
          <EventCard {...event} schedule={eventSchedule} />
        </EventCardContainer>
      )}
    </LowMarginCard>
  );
});
GenericCardContainer.displayName = "GenericCardContainer";
GenericCardContainer.propTypes = {
  id: PropTypes.number.isRequired,
  status: PropTypes.oneOf(Object.values(ACTIVITY_STATUS)),
  type: PropTypes.string.isRequired,
  event: PropTypes.object, // see event card PropTypes
  timestamp: PropTypes.string.isRequired,
  children: PropTypes.node,
  config: PropTypes.shape({
    icon: PropTypes.string,
    hasEvent: PropTypes.bool,
    action: PropTypes.func,
    hideDate: PropTypes.bool,
  }),
};

export default GenericCardContainer;
