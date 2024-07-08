import React, { useMemo, useState } from "react";
import styled from "styled-components";
import useSWR from "swr";
import useSWRImmutable from "swr/immutable";

import BackLink from "@agir/front/app/Navigation/BackLink";
import Button from "@agir/front/genericComponents/Button";
import RadioField from "@agir/front/formComponents/RadioField";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";
import EventCardList from "./EventCardList";
import EventTextList from "./EventTextList";
import GroupSelectField from "./GroupSelectField";
import ZipCodeSelectField from "./ZipCodeSelectField";

import { TIMING_OPTIONS } from "./common";
import { useLocationState } from "@agir/front/app/hooks";
import { getGroupEndpoint } from "@agir/groups/utils/api";
import { getGroupUpcomignEventEndpoint } from "./api";

const StyledResults = styled.div`
  display: flex;
  flex-flow: row nowrap;
  gap: 4rem;
  justify-content: space-between;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    flex-direction: column;
  }

  & > * {
    flex: 1 1 100%;
    max-width: calc(50% - 2rem);

    @media (max-width: ${(props) => props.theme.collapse}px) {
      max-width: 100%;
    }
  }
`;

const StyledPage = styled.main`
  padding: 2rem;
  max-width: 70rem;
  margin: 0 auto;
  min-height: 50vh;

  @media (max-width: ${(props) => props.theme.collapse}px) {
    padding: 1.5rem;
    max-width: 100%;
    min-height: calc(100vh - 300px);
  }

  nav {
    display: flex;
    justify-content: space-between;
    align-items: center;

    & > * {
      margin: 0;
    }

    strong {
      font-weight: inherit;
      text-decoration: underline;
    }

    @media (max-width: ${(props) => props.theme.collapse}px) {
      display: none;
    }
  }

  h2 {
    font-size: 1.625rem;
    font-weight: 700;
    margin: 2rem 0 1rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 1.375rem;
      margin: 0 0 1.25rem;
    }
  }

  h4 {
    margin: 0;
    font-size: 1.125rem;
    font-weight: 700;
    line-height: 1.4;
  }

  h6 {
    color: ${(props) => props.theme.text700};
    font-size: 1rem;
    margin: 1.5rem 0 0.5rem;

    &::first-letter {
      text-transform: uppercase;
    }

    &:first-of-type {
      margin-top: 0;
    }
  }

  em {
    font-style: normal;
    font-size: 0.875rem;
    color: ${(props) => props.theme.text700};
  }
`;

const GroupUpcomingEventPage = () => {
  const [params, setParams, clearParams] = useLocationState();
  const [timing, setTiming] = useState(TIMING_OPTIONS[0].value);

  const { data: zipCodes, isLoading: isLoadingZipCodes } = useSWRImmutable(
    "/api/codes-postaux/",
  );
  const { data: groups, isLoading: isLoadingGroups } = useSWRImmutable(
    () =>
      !isLoadingZipCodes &&
      params.z &&
      getGroupEndpoint("geoSearchGroups", null, { zip: params.z }),
    {
      keepPreviousData: !!params.z,
    },
  );
  const { data: events, isLoading: isLoadingEvents } = useSWR(
    () =>
      !!params.g &&
      getGroupUpcomignEventEndpoint("groupUpcomingEvents", null, {
        groups: params.g,
        timing,
      }),
  );

  const displayZips = useMemo(
    () => Array.isArray(params.z) && params.z.length > 1,
    [params.z],
  );

  return (
    <PageFadeIn ready={!isLoadingZipCodes} wait={<Skeleton />}>
      {!isLoadingZipCodes && (
        <StyledPage>
          <nav>
            <BackLink />
          </nav>
          <h2>Agenda des groupes d’action</h2>
          <div
            css={`
              text-align: right;
            `}
          >
            <Button
              small
              icon="refresh-cw"
              color="choose"
              onClick={clearParams}
              disabled={
                isLoadingEvents ||
                isLoadingGroups ||
                typeof clearParams !== "function"
              }
            >
              Réinitialiser
            </Button>
          </div>
          <ZipCodeSelectField
            value={params}
            onChange={setParams}
            zipCodes={zipCodes}
            isLoading={isLoadingGroups}
          />
          <Spacer size="1.5rem" />
          <GroupSelectField
            label={<h4>Groupe{groups?.length > 0 ? "s" : ""} d'action</h4>}
            value={params}
            onChange={setParams}
            groups={groups}
            isLoading={isLoadingGroups}
            disabled={isLoadingEvents}
            displayZips={displayZips}
          />
          <Spacer size="1.5rem" />
          <h4>Période</h4>
          <Spacer size="1rem" />
          <RadioField
            value={timing}
            onChange={setTiming}
            options={TIMING_OPTIONS}
            aria-label="Période"
            disabled={isLoadingEvents}
          />
          <Spacer size="1.5rem" />
          <hr />
          <Spacer size="1.5rem" />
          <StyledResults>
            <div>
              <h4>Événements</h4>
              <Spacer size="1rem" />
              <EventCardList
                events={events}
                isLoading={isLoadingEvents}
                disabled={!params.g}
                backLink={{
                  route: "groupUpcomingEvents",
                  params,
                }}
              />
            </div>
            {events && events.length > 0 && (
              <div>
                <h4>Message récapitulatif de l’agenda</h4>
                <Spacer size="1rem" />
                <EventTextList
                  events={events}
                  timing={timing}
                  displayZips={displayZips}
                />
              </div>
            )}
          </StyledResults>
        </StyledPage>
      )}
    </PageFadeIn>
  );
};

GroupUpcomingEventPage.propTypes = {};

export default GroupUpcomingEventPage;
