import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import { Interval, DateTime } from "luxon";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes, getIsConnected } from "@agir/front/globalContext/reducers";

import Button from "@agir/front/genericComponents/Button";
import style from "@agir/front/genericComponents/_variables.scss";
import { Hide } from "@agir/front/genericComponents/grid";
import CSRFProtectedForm from "@agir/front/genericComponents/CSRFProtectedForm";
import { displayHumanDate } from "@agir/lib/utils/time";

const EventHeaderContainer = styled.div`
  @media (min-width: ${style.collapse}px) {
    margin-bottom: 4rem;
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
const ActionLink = styled.a`
  font-weight: 700;
  text-decoration: underline;
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

const ActionButtons = (props) => {
  const {
    hasSubscriptionForm,
    past,
    rsvped,
    logged,
    isOrganizer,
    routes,
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
      <StyledActionButtons>
        <ActionButton icon="check" color="confirmed">
          Je participe
        </ActionButton>
        {isOrganizer && (
          <ActionButton icon="settings" as="a" href={routes.manage}>
            Gérer l'événement
          </ActionButton>
        )}
      </StyledActionButtons>
    );
  }

  if (hasSubscriptionForm) {
    return (
      <StyledActionButtons>
        <ActionButton as="a" color="secondary" href={`${routes.rsvp}`}>
          Participer à l'événement
        </ActionButton>
      </StyledActionButtons>
    );
  }

  return (
    <StyledActionButtons>
      <CSRFProtectedForm method="post" action={routes.rsvp}>
        <ActionButton type="submit" color="secondary">
          Participer à l'événement
        </ActionButton>
      </CSRFProtectedForm>
    </StyledActionButtons>
  );
};
ActionButtons.propTypes = {
  hasSubscriptionForm: PropTypes.bool,
  past: PropTypes.bool,
  rsvped: PropTypes.bool,
  logged: PropTypes.bool,
  isOrganizer: PropTypes.bool,
  routes: PropTypes.shape({
    manage: PropTypes.string,
    rsvp: PropTypes.string,
  }),
};

const AdditionalMessage = ({ logged, rsvped, price, routes, forUsers }) => {
  if (!logged) {
    return (
      <div>
        <ActionLink href={routes.login}>Je me connecte</ActionLink> ou{" "}
        <ActionLink href={`${routes.join}?type=${forUsers}`}>
          je m'inscris
        </ActionLink>{" "}
        pour participer à l'événement
      </div>
    );
  }

  if (rsvped) {
    return (
      <SmallText>
        <a href={routes.cancel}>Annuler ma participation</a>
      </SmallText>
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

  return (
    <SmallText>Votre email sera communiqué à l'organisateur·ice</SmallText>
  );
};
AdditionalMessage.propTypes = {
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
  name,
  rsvp,
  options,
  schedule,
  routes,
  isOrganizer,
  hasSubscriptionForm,
  forUsers,
}) => {
  const globalRoutes = useSelector(getRoutes);
  const logged = useSelector(getIsConnected);

  const rsvped = rsvp === "CO";
  const now = DateTime.local();
  const past = now > schedule.end;
  let eventString = displayHumanDate(schedule.start);
  eventString = eventString.slice(0, 1).toUpperCase() + eventString.slice(1);

  return (
    <EventHeaderContainer>
      <EventTitle>{name}</EventTitle>
      <Hide under>
        <EventDate>{eventString}</EventDate>
      </Hide>
      <ActionButtons
        hasSubscriptionForm={hasSubscriptionForm}
        past={past}
        logged={logged}
        rsvped={rsvped}
        routes={routes}
        isOrganizer={isOrganizer}
        forUsers={forUsers}
      />
      {!past && (
        <AdditionalMessage
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
  name: PropTypes.string,
  schedule: PropTypes.instanceOf(Interval),
  hasSubscriptionForm: PropTypes.bool,
  isOrganizer: PropTypes.bool,
  options: PropTypes.shape({
    price: PropTypes.string,
  }),
  rsvp: PropTypes.string,
  routes: PropTypes.object,
  forUsers: PropTypes.string,
  canRSVP: PropTypes.bool,
};

export default EventHeader;
