import { DateTime, Interval } from "luxon";
import PropTypes from "prop-types";
import React, { useCallback, useMemo, useState } from "react";
import { useLocation } from "react-router-dom";
import styled from "styled-components";
import { mutate } from "swr";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getIsConnected,
  getRoutes,
  getUser,
} from "@agir/front/globalContext/reducers";
import * as api from "@agir/events/common/api";

import Button from "@agir/front/genericComponents/Button";
import Link from "@agir/front/app/Link";
import { Hide } from "@agir/front/genericComponents/grid";
import SubscriptionTypeModal from "@agir/front/authentication/SubscriptionTypeModal";

import style from "@agir/front/genericComponents/_variables.scss";
import { displayHumanDate, displayIntervalEnd } from "@agir/lib/utils/time";

import QuitEventButton from "./QuitEventButton";

import logger from "@agir/lib/utils/logger";

const log = logger(__filename);

const EventHeaderContainer = styled.div`
  @media (min-width: ${style.collapse}px) {
    margin-bottom: 2rem;
  }
  > * {
    margin: 0.5rem 0;
  }
`;

const EventTitle = styled.h1`
  font-size: 1.75rem;
  line-height: 1.4;
  font-weight: 700;
  margin-bottom: 0;

  @media (max-width: ${style.collapse}px) {
    margin-bottom: 1rem;
    font-size: 1.25rem;
  }
`;

const EventDate = styled.div`
  margin: 0.5rem 0;
  font-weight: 500;
`;

const SmallText = styled.div`
  font-size: 0.81rem;
  font-color: ${style.black500};
`;

const ActionButton = styled(Button)``;
const ActionLink = styled(Link)`
  font-weight: 700;
  text-decoration: underline;
`;
const ActionDetails = styled.div`
  margin-top: 0;
  font-size: 1rem;
  display: flex;
  align-items: center;
  flex-wrap: wrap;

  div {
    display: inline-flex;
    align-items: center;
  }
`;

const StyledActionButtons = styled.div`
  display: inline-grid;
  grid-gap: 0.5rem;
  grid-template-columns: auto auto;
  padding: 0.5rem 0;

  @media (max-width: ${style.collapse}px) {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }

  ${Button} {
    margin: 0;
    justify-content: center;

    && *,
    && *::before {
      flex: 0 0 auto;
    }
  }

  ${Button} + ${Button} {
    margin-left: 0;
  }
`;

const RSVPButton = (props) => {
  const user = useSelector(getUser);
  const { id, forUsers, hasPrice, routes, hasSubscriptionForm } = props;

  const [isLoading, setIsLoading] = useState(false);
  const [hasSubscriptionTypeModal, setHasSubscriptionTypeModal] =
    useState(false);

  const openSubscriptionTypeModal = useCallback(() => {
    setHasSubscriptionTypeModal(true);
  }, []);

  const closeSubscriptionTypeModal = useCallback(() => {
    setHasSubscriptionTypeModal(false);
  }, []);

  const handleRSVP = useCallback(
    async (e) => {
      e && e.preventDefault();
      setIsLoading(true);

      if (hasPrice || hasSubscriptionForm) {
        log.debug("Has price or subscription form, redirection.");
        window.location.href = routes.rsvp;
        return;
      }

      try {
        const response = await api.rsvpEvent(id);
        if (response.error) {
          log.error(response.error);
          await mutate(api.getEventEndpoint("getEvent", { eventPk: id }));
        }
      } catch (err) {
        window.location.reload();
      }

      setIsLoading(false);
      setHasSubscriptionTypeModal(false);

      await mutate(
        api.getEventEndpoint("getEvent", { eventPk: id }),
        (event) => ({
          ...event,
          rsvped: true,
        })
      );
    },
    [id, hasPrice, routes]
  );

  const shouldUpdateSubscription = useMemo(() => {
    if (!user) {
      return null;
    }
    if (forUsers === "2" && user.is2022) {
      return null;
    }
    if (forUsers === "I" && user.isInsoumise) {
      return null;
    }
    return forUsers === "2" ? "NSP" : "LFI";
  }, [user, forUsers]);

  return (
    <StyledActionButtons>
      <ActionButton
        type="submit"
        color="secondary"
        disabled={isLoading}
        onClick={
          shouldUpdateSubscription ? openSubscriptionTypeModal : handleRSVP
        }
      >
        Participer à l'événement
      </ActionButton>
      {shouldUpdateSubscription ? (
        <SubscriptionTypeModal
          shouldShow={hasSubscriptionTypeModal}
          type={shouldUpdateSubscription}
          target="event"
          onConfirm={handleRSVP}
          onCancel={closeSubscriptionTypeModal}
          isLoading={isLoading}
        />
      ) : null}
    </StyledActionButtons>
  );
};

const ActionButtons = (props) => {
  const {
    id,
    name,
    past,
    rsvped,
    logged,
    isOrganizer,
    routes,
    onlineUrl,
    hasPrice,
    allowGuests,
    hasSubscriptionForm,
  } = props;

  if (past) {
    return (
      <StyledActionButtons>
        <Button disabled color="unavailable">
          Événement terminé
        </Button>
        {isOrganizer && (
          <ActionButton icon="settings" as="a" href={routes.manage}>
            Gérer l'événement
          </ActionButton>
        )}
      </StyledActionButtons>
    );
  }

  if (!logged) {
    return (
      <StyledActionButtons>
        <ActionButton color="secondary" disabled={true}>
          Participer à l'événement
        </ActionButton>
      </StyledActionButtons>
    );
  }

  if (rsvped) {
    return (
      <>
        <StyledActionButtons>
          {!!onlineUrl && (
            <ActionButton
              icon="video"
              as="a"
              href={onlineUrl}
              target="_blank"
              color="primary"
            >
              Rejoindre en ligne
            </ActionButton>
          )}
          {isOrganizer && (
            <ActionButton icon="settings" as="a" href={routes.manage}>
              Gérer l'événement
            </ActionButton>
          )}
          {allowGuests && hasSubscriptionForm && (
            <ActionButton as="a" href={routes.rsvp} type="submit">
              Ajouter une personne
            </ActionButton>
          )}
        </StyledActionButtons>
        <ActionDetails>
          <div>
            <RawFeatherIcon name="check" color="green" /> &nbsp;Vous participez
            à l'évènement
          </div>
          &nbsp;&nbsp;
          {!hasPrice && <QuitEventButton id={id} name={name} />}
        </ActionDetails>
      </>
    );
  }

  return <RSVPButton {...props} />;
};
RSVPButton.propTypes = ActionButtons.propTypes = {
  id: PropTypes.string,
  name: PropTypes.string,
  onlineUrl: PropTypes.string,
  hasSubscriptionForm: PropTypes.bool,
  hasPrice: PropTypes.bool,
  past: PropTypes.bool,
  rsvped: PropTypes.bool,
  logged: PropTypes.bool,
  isOrganizer: PropTypes.bool,
  routes: PropTypes.shape({
    manage: PropTypes.string,
    rsvp: PropTypes.string,
  }),
};

const AdditionalMessage = ({
  isOrganizer,
  logged,
  rsvped,
  price,
  forUsers,
}) => {
  const location = useLocation();

  if (!logged) {
    return (
      <div>
        <ActionLink
          route="login"
          params={{ from: "event", forUsers, next: location.pathname }}
        >
          Je me connecte
        </ActionLink>{" "}
        ou{" "}
        <ActionLink
          route="signup"
          params={{ from: "event", forUsers, next: location.pathname }}
        >
          je m'inscris
        </ActionLink>{" "}
        pour participer à l'événement
      </div>
    );
  }

  if (price) {
    return (
      <SmallText>
        <strong>Entrée&nbsp;: </strong>
        {price}
      </SmallText>
    );
  }

  if (!isOrganizer && !rsvped) {
    return (
      <SmallText>Votre email sera communiqué à l'organisateur·ice</SmallText>
    );
  }

  return <></>;
};
AdditionalMessage.propTypes = {
  id: PropTypes.string,
  name: PropTypes.string,
  hasSubscriptionForm: PropTypes.bool,
  past: PropTypes.bool,
  rsvped: PropTypes.bool,
  logged: PropTypes.bool,
  isOrganizer: PropTypes.bool,
  price: PropTypes.string,
  routes: PropTypes.object,
  forUsers: PropTypes.string,
};

const EventHeader = ({
  id,
  name,
  rsvp,
  options,
  schedule,
  routes,
  isOrganizer,
  forUsers,
  hasRightSubscription,
  onlineUrl,
  allowGuests,
  hasSubscriptionForm,
}) => {
  const globalRoutes = useSelector(getRoutes);
  const logged = useSelector(getIsConnected);

  const rsvped = rsvp === "CO";
  const now = DateTime.local();
  const past = now > schedule.end;
  let eventString = displayHumanDate(schedule.start);
  eventString = eventString.slice(0, 1).toUpperCase() + eventString.slice(1);

  const pending = now >= schedule.start && now <= schedule.end;
  const eventDate = pending ? displayIntervalEnd(schedule) : eventString;

  return (
    <EventHeaderContainer>
      <EventTitle>{name}</EventTitle>
      <Hide under>
        <EventDate>{eventDate}</EventDate>
      </Hide>
      <ActionButtons
        id={id}
        past={past}
        logged={logged}
        rsvped={rsvped}
        routes={routes}
        isOrganizer={isOrganizer}
        forUsers={forUsers}
        hasRightSubscription={hasRightSubscription}
        hasPrice={!!options && !!options.price}
        onlineUrl={onlineUrl}
        allowGuests={allowGuests}
        hasSubscriptionForm={hasSubscriptionForm}
      />
      {!past && (
        <AdditionalMessage
          id={id}
          name={name}
          isOrganizer={isOrganizer}
          past={past}
          logged={logged}
          rsvped={rsvped}
          price={options.price}
          routes={{ ...routes, ...globalRoutes }}
          forUsers={forUsers}
        />
      )}
    </EventHeaderContainer>
  );
};

EventHeader.propTypes = {
  id: PropTypes.string,
  name: PropTypes.string,
  onlineUrl: PropTypes.string,
  startTime: PropTypes.instanceOf(DateTime),
  endTime: PropTypes.instanceOf(DateTime),
  schedule: PropTypes.instanceOf(Interval),
  hasSubscriptionForm: PropTypes.bool,
  isOrganizer: PropTypes.bool,
  options: PropTypes.shape({
    price: PropTypes.string,
  }),
  rsvp: PropTypes.string,
  routes: PropTypes.object,
  forUsers: PropTypes.string,
  hasRightSubscription: PropTypes.bool,
  allowGuests: PropTypes.bool,
};

export default EventHeader;
