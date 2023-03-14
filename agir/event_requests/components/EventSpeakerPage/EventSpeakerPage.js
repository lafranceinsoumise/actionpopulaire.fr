import React from "react";
import styled from "styled-components";

import { useEventSpeaker } from "@agir/event_requests/common/hooks";

import BottomBar from "@agir/front/app/Navigation/BottomBar";
import ErrorPage from "@agir/front/errorPage/ErrorPage";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Spacer from "@agir/front/genericComponents/Spacer";
import UpcomingEvents from "@agir/events/common/UpcomingEvents";
import { Hide, useResponsiveMemo } from "@agir/front/genericComponents/grid";

import EventRequestCard from "./EventRequestCard";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";

const StyledRequestCardList = styled.div`
  display: flex;
  flex-flow: column nowrap;
  gap: 1rem;
`;

const StyledPage = styled.div`
  width: 100%;
  max-width: 1442px;
  margin: 0 auto;
  padding: 3rem 4rem;
  min-height: calc(100vh - 420px);

  @media (max-width: ${(props) => props.theme.collapse}px) {
    padding: 1rem 1rem 3rem;
    background-color: ${(props) => props.theme.black25};
  }

  h3 {
    font-weight: 600;
    margin: 0 0 1rem;
    font-size: 2rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 1.5rem;
    }
  }

  main {
    display: flex;
    gap: 4rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      flex-direction: column-reverse;
      gap: 1.5rem;
    }

    section,
    aside {
      & h4 {
        font-weight: 600;
        margin: 0 0 1rem;
        font-size: 1.125rem;
      }

      & p {
        font-size: 0.875rem;
        color: ${(props) => props.theme.black700};
      }
    }

    section {
      flex: 1 1 auto;
    }
  }
`;

const EventSpeakerPage = () => {
  const { speaker, requests, events, isLoading, isLoadingEvents } =
    useEventSpeaker();

  const upcomingEventOrientation = useResponsiveMemo("horizontal", "vertical");

  if (!isLoading && !speaker) {
    return (
      <ErrorPage
        title="Vous n'êtes pas autorisé·e à accéder à cette page"
        subtitle="Si vous êtes arrivé·e ici en suivant un lien reçu par e-mail, vérifiez que vous êtes bien connecté·e avec le compte correspondant à la même adresse e-mail."
        icon={<RawFeatherIcon name="lock" />}
        hasTopBar={false}
        hasReload={false}
      />
    );
  }

  const hasEvents = Array.isArray(events) && events.length > 0;
  const hasAnswerable =
    Array.isArray(requests.answerable) && requests.answerable.length > 0;
  const hasUnanswerable =
    Array.isArray(requests.unanswerable) && requests.unanswerable.length > 0;

  return (
    <PageFadeIn ready={!isLoading}>
      <StyledPage>
        <Hide over as="h3">
          Demandes d'événements
        </Hide>
        <main>
          <section>
            <Hide under as="h3">
              Demandes d'événements
            </Hide>
            {!hasAnswerable && !hasUnanswerable ? (
              <p>Vous n'avez pas encore reçu de demandes d'événement.</p>
            ) : (
              <>
                <h4>Demandes en cours</h4>
                {hasAnswerable ? (
                  <StyledRequestCardList>
                    {requests.answerable.map((request) => (
                      <EventRequestCard key={request.id} {...request} />
                    ))}
                  </StyledRequestCardList>
                ) : (
                  <p>Vous n'avez pas de demande à traiter.</p>
                )}

                {hasUnanswerable && (
                  <>
                    <Spacer size="1.5rem" />
                    <h4>Demandes passées</h4>
                    <StyledRequestCardList>
                      {requests.unanswerable.map((request) => (
                        <EventRequestCard key={request.id} {...request} />
                      ))}
                    </StyledRequestCardList>
                  </>
                )}
              </>
            )}
          </section>
          <Hide under={!hasEvents} as="aside">
            <PageFadeIn ready={!isLoadingEvents}>
              <h4>Vos événements à venir</h4>
              {hasEvents ? (
                <UpcomingEvents
                  orientation={upcomingEventOrientation}
                  events={events}
                  backLink="eventSpeaker"
                />
              ) : (
                <p>Vous n'avez pas d'événements à venir</p>
              )}
            </PageFadeIn>
          </Hide>
        </main>
      </StyledPage>
      <Hide over>
        <BottomBar />
      </Hide>
    </PageFadeIn>
  );
};

export default EventSpeakerPage;
