import { DateTime, Interval } from "luxon";
import PropTypes from "prop-types";
import React, { useCallback, useState } from "react";
import { useLocation } from "react-router-dom";
import styled from "styled-components";
import { mutate } from "swr";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getIsConnected, getRoutes } from "@agir/front/globalContext/reducers";
import * as api from "@agir/events/common/api";

import Button from "@agir/front/genericComponents/Button";
import Link from "@agir/front/app/Link";
import { Hide } from "@agir/front/genericComponents/grid";

import style from "@agir/front/genericComponents/_variables.scss";
import { displayHumanDate, displayIntervalEnd } from "@agir/lib/utils/time";
import { routeConfig } from "@agir/front/app/routes.config";

import QuitEventButton from "./QuitEventButton";
import Modal from "@agir/front/genericComponents/Modal";
import Spacer from "@agir/front/genericComponents/Spacer";
import StaticToast from "@agir/front/genericComponents/StaticToast";

import logger from "@agir/lib/utils/logger";

import { getUser } from "@agir/front/globalContext/reducers";

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

const StyledActions = styled.div`
  display: inline-grid;
  grid-gap: 0.5rem;
  grid-template-columns: auto auto;
  padding: 0.5rem 0;

  @media (max-width: ${style.collapse}px) {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(200px, 1fr));
  }
`;

const ModalContent = styled.div`
  background: white;
  max-width: 500px;
  padding: 10px 20px;
  height: 50%;
  width: 50%;
  overflow: auto;
  margin: 5% auto;
  display: flex;
  flex-direction: column;
  border-radius: ${style.borderRadius};

  h2 {
    font-size: 18px;
    margin-top: 0;
  }

  @media(max-width: ${style.collapse}px) {
    width: 100vw;
    height: 100vh;
    margin: 0;
    border-radius: 0;
  }
`;

const StyledIconButton = styled.button`
  display: flex;
  align-items: center;
  justify-content: center;
  height: 2rem;
  width: 2rem;
  border: none;
  padding: 0;
  margin: 0;
  text-decoration: none;
  background: inherit;
  cursor: pointer;
  text-align: center;
  -webkit-appearance: none;
  -moz-appearance: none;
  color: ${style.black1000};
`;

const StyledModalHeader = styled.header`
  display: ${({ $mobile }) => ($mobile ? "none" : "flex")};
  justify-content: end;

  @media (max-width: ${style.collapse}px) {
    display: ${({ $mobile }) => ($mobile ? "flex" : "none")};
    justify-content: end;
  }
`;

const GroupItem = styled.div`
  display: flex;
  align-items: center;
  cursor: pointer;

  :hover {
    opacity: 0.8;
  }

  ${RawFeatherIcon} {
    flex: 0 0 auto;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2rem;
    height: 2rem;
    background-color: ${style.primary500};
    color: #fff;
    clip-path: circle(1rem);
    text-align: center;
    margin-right: 0.5rem;
  }
`;

const JoiningDetails = ({ id, name, hasPrice, rsvped, groups }) => {

  return <StaticToast $color="green" style={{ borderRadius: style.borderRadius, borderColor: "lightgrey" }}>
      <RawFeatherIcon name="check" color="green" /> &nbsp;Vous participez
      à l'événement
    {!hasPrice && <>
    {/* <Spacer size="1rem" style={{ display: "inline-block" }} /> */}
    &nbsp;&nbsp;
    <QuitEventButton id={id} name={name} />
    </>}
  </StaticToast>;
};

const RSVPButton = (props) => {
  const { id, hasPrice, routes, hasSubscriptionForm, isOrganizer } = props;

  const [isLoading, setIsLoading] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [errors, setErrors] = useState({});
  const [success, setSuccess] = useState(false);

  // Get groups where im manager
  const user = useSelector(getUser);
  // console.log("user groups ", user?.groups);

  // TODO : Get groups already attendees of the event
  const managingGroups = user?.groups.filter(
    (group) => true || (group.id !== id && group.isManager)
  );
  console.log("managing groups : ", managingGroups);

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

      await mutate(
        api.getEventEndpoint("getEvent", { eventPk: id }),
        (event) => ({
          ...event,
          rsvped: true,
        })
      );
    },
    [id, hasPrice, routes, hasSubscriptionForm]
  );

  // If has groups : show groups that im manager who can join
  const handleJoinAsGroup = async (groupPk) => {
    setErrors({});
    const { data, error } = await api.joinEventAsGroup(id, groupPk);

    console.log("data error ", data, error);
    if (error) {
      setErrors(error);
      return;
    }
    setSuccess(true);
  };

  const showModalJoinAsGroup = () => {
    setIsModalOpen(true);
  };

  const closeModalJoin = () => {
    setSuccess(false);
    setIsModalOpen(false);
    setErrors({});
  };

  return (
    <StyledActions>
      <Button
        type="submit"
        color="primary"
        loading={isLoading}
        disabled={isLoading}
        onClick={handleRSVP}
      >
        Participer à l'événement
      </Button>

      {!!managingGroups?.length && (
        <Button
          loading={isLoading}
          disabled={isLoading}
          onClick={showModalJoinAsGroup}
        >
          Ajouter un groupe participant
        </Button>
      )}
      {isOrganizer && (
        <Button
          icon="settings"
          link
          to={routeConfig.eventSettings.getLink({ eventPk: id })}
          color="primary"
        >
          Gérer l'événement
        </Button>
      )}
      {!!managingGroups?.length && (
        <Modal
          shouldShow={isModalOpen}
          isOpen={isModalOpen}
          onClose={closeModalJoin}
          onDismiss={closeModalJoin}
          shouldDismissOnClick
          noScroll
        >
          <ModalContent>
            <StyledModalHeader>
              <StyledIconButton onClick={closeModalJoin}>
                <RawFeatherIcon name="x" />
              </StyledIconButton>
            </StyledModalHeader>
            {!success ? (
              <>
                <h2>Ajouter un groupe participant</h2>
                Ajoutez un groupe dont vous êtes gestionnaire comme participant
                à l’événement.
                <Spacer size="0.5rem" />
                L’événement sera à ajouté à l’agenda du groupe.
                <Spacer size="1rem" />
                {managingGroups.map((group) => (
                  <GroupItem
                    key={group.id}
                    onClick={() => handleJoinAsGroup(group.id)}
                  >
                    <RawFeatherIcon width="1rem" height="1rem" name="users" />
                    <div>{group.name}</div>
                  </GroupItem>
                ))}
                <Spacer size="1rem" />
                {!!Object.keys(errors).length && (errors?.text || "Une erreur est apparue")}
              </>
            ) : (
              <>
                <h2 style={{ color: style.green500 }}>
                  Votre groupe participe à l’évémenent&nbsp;!
                </h2>
                {success} est désormais indiqué comme
                participant à l’événement.
                <Spacer size="1rem" />
                Tous les membres du groupe présents doivent également indiquer
                leur présence individuelle sur Action Populaire pour aider les
                organisateur·ices à définir le nombre de participants.
                <Spacer size="1rem" />
                <Button onClick={closeModalJoin}>Compris</Button>
              </>
            )}
          </ModalContent>
        </Modal>
      )}

      <JoiningDetails id={id} name={"hello"} hasPrice={false} rsvped={true} groups={[]} />
    </StyledActions>
  );
};

const Actions = (props) => {
  const {
    id,
    name,
    past,
    rsvped,
    logged,
    isOrganizer,
    routes,
    hasPrice,
    allowGuests,
    hasSubscriptionForm,
  } = props;

  if (past) {
    return (
      <StyledActions>
        <Button disabled color="unavailable">
          Événement terminé
        </Button>
        {isOrganizer && (
          <Button
            icon="settings"
            link
            to={routeConfig.eventSettings.getLink({ eventPk: id })}
            color="primary"
          >
            Gérer l'événement
          </Button>
        )}
      </StyledActions>
    );
  }

  if (!logged) {
    return (
      <StyledActions>
        <Button color="secondary" disabled={true}>
          Participer à l'événement
        </Button>
      </StyledActions>
    );
  }

  if (rsvped) {
    return (
      <>
        <StyledActions>
          {isOrganizer && (
            <Button
              icon="settings"
              link
              to={routeConfig.eventSettings.getLink({ eventPk: id })}
              color="primary"
            >
              Gérer l'événement
            </Button>
          )}
          {allowGuests && (hasSubscriptionForm || hasPrice) && (
            <Button link href={routes.rsvp}>
              Ajouter une personne
            </Button>
          )}
        </StyledActions>
        {/* <ActionDetails>
          <div>
            <RawFeatherIcon name="check" color="green" /> &nbsp;Vous participez
            à l'évènement
          </div>
          &nbsp;&nbsp;
          {!hasPrice && <QuitEventButton id={id} name={name} />}
        </ActionDetails> */}
        <JoiningDetails id={id} name={name} hasPrice={hasPrice} rsvped={rsvped} groups={[]} />
      </>
    );
  }

  return <RSVPButton {...props} />;
};
RSVPButton.propTypes = Actions.propTypes = {
  id: PropTypes.string,
  name: PropTypes.string,
  hasSubscriptionForm: PropTypes.bool,
  hasPrice: PropTypes.bool,
  past: PropTypes.bool,
  rsvped: PropTypes.bool,
  logged: PropTypes.bool,
  isOrganizer: PropTypes.bool,
  allowGuests: PropTypes.bool,
  routes: PropTypes.shape({
    manage: PropTypes.string,
    rsvp: PropTypes.string,
  }),
};

const AdditionalMessage = ({ isOrganizer, logged, rsvped, price }) => {
  const location = useLocation();

  if (!logged) {
    return (
      <div>
        <ActionLink
          route="login"
          state={{ from: "event", next: location.pathname }}
        >
          Je me connecte
        </ActionLink>{" "}
        ou{" "}
        <ActionLink
          route="signup"
          state={{ from: "event", next: location.pathname }}
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
};

const EventHeader = ({
  id,
  name,
  rsvp,
  options,
  schedule,
  routes,
  isOrganizer,
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
      <Actions
        id={id}
        past={past}
        logged={logged}
        rsvped={rsvped}
        routes={routes}
        isOrganizer={isOrganizer}
        hasPrice={!!options && !!options.price}
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
        />
      )}
    </EventHeaderContainer>
  );
};

EventHeader.propTypes = {
  id: PropTypes.string,
  name: PropTypes.string,
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
  allowGuests: PropTypes.bool,
};

export default EventHeader;
