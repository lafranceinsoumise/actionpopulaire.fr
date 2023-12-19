import _sortBy from "lodash/sortBy";
import PropTypes from "prop-types";
import React, { useMemo, useState } from "react";
import styled from "styled-components";
import useSWR from "swr";

import style from "@agir/front/genericComponents/_variables.scss";

import EventTextList from "@agir/events/groupUpcomingEventPage/EventTextList";
import RadioField from "@agir/front/formComponents/RadioField";
import Button from "@agir/front/genericComponents/Button";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel";
import {
  StyledSubtitle,
  StyledTitle,
} from "@agir/front/genericComponents/ObjectManagement/styledComponents";
import Spacer from "@agir/front/genericComponents/Spacer.js";

import { getGroupUpcomignEventEndpoint } from "@agir/events/groupUpcomingEventPage/api";
import {
  TIMING_OPTIONS,
  groupUpcomingEventLinkForGroup,
} from "@agir/events/groupUpcomingEventPage/common";
import { useGroup } from "@agir/groups/groupPage/hooks/group.js";

import EventCardList from "@agir/events/groupUpcomingEventPage/EventCardList";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";

const Skeleton = styled.div`
  height: 36px;
  margin-bottom: 10px;
  width: 50%;
  background-color: ${style.black50};
`;

const StyledHeading = styled.nav`
  display: flex;
  flex-flow: row wrap;
  align-items: center;
  justify-content: start;
  font-size: 0.875rem;
  line-height: 1.5;
  margin-bottom: 0.25rem;

  & > * {
    flex: 0 0 auto;
    width: auto;

    &:first-child {
      margin-right: auto;
    }
  }
`;

const StyledContent = styled.div`
  color: ${(props) => props.theme.black700};

  em {
    font-style: normal;
  }
`;

const StyledEmptySpace = styled.p`
  margin-top: 1rem;
  font-size: 0.875rem;
  text-align: center;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 1.5rem;
  border: 1px solid ${(props) => props.theme.black50};

  @media (max-width: ${(props) => props.theme.collapse}px) {
    padding: 1rem;

    ${Button} {
      font-size: 0.875rem;
    }
  }
`;

const GroupUpcomingEventPage = (props) => {
  const { onBack, illustration, groupPk, route } = props;
  const group = useGroup(groupPk);

  const [timing, setTiming] = useState(TIMING_OPTIONS[0].value);

  const { data: events, isLoading } = useSWR(
    () =>
      getGroupUpcomignEventEndpoint("groupUpcomingEvents", null, {
        groups: groupPk,
        timing,
      }),
    {
      keepPreviousData: true,
    },
  );

  const groupUpcomingEventLink = useMemo(
    () => group && groupUpcomingEventLinkForGroup(group),
    [group],
  );

  return (
    <>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledHeading>
        <StyledTitle>Agenda</StyledTitle>
        {groupUpcomingEventLink && (
          <Button
            icon="external-link"
            color="link"
            link
            to={groupUpcomingEventLink}
            target="_blank"
            small
            $wrap
            backLink={{ to: route.getLink(), label: group.name }}
          >
            Agenda des GA à proximité
          </Button>
        )}
      </StyledHeading>
      <span style={{ color: style.black700 }}>
        Retrouvez une liste de tous les événements à venir organisés et
        co-organisés par votre groupe pour la semaine ou le mois, facilement
        diffusable.
      </span>
      <Spacer size="1rem" />
      <RadioField
        label="Période"
        value={timing}
        onChange={setTiming}
        options={TIMING_OPTIONS}
        aria-label="Période"
        disabled={isLoading}
      />
      <Spacer size="1rem" />
      <StyledContent>
        <PageFadeIn ready={!isLoading} wait={<Skeleton boxes={1} />}>
          {events && events.length > 0 ? (
            <>
              <EventCardList
                events={events}
                isLoading={isLoading}
                backLink={{ to: route.getLink(), label: group.name }}
              />
              <hr />
              <StyledSubtitle>Message récapitulatif de l’agenda</StyledSubtitle>
              <Spacer size="1rem" />
              <EventTextList events={events} timing={timing} />
            </>
          ) : (
            <StyledEmptySpace>
              Il n’y a pas d’événement prévu dans votre groupe pour la période
              sélectionnée
              <br />
              <Button
                link
                route="createEvent"
                params={{ group: groupPk }}
                color="secondary"
                icon="plus"
              >
                Créer un événement
              </Button>
            </StyledEmptySpace>
          )}
        </PageFadeIn>
      </StyledContent>
    </>
  );
};
GroupUpcomingEventPage.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  groupPk: PropTypes.string,
  route: PropTypes.shape({
    getLink: PropTypes.func,
  }),
};
export default GroupUpcomingEventPage;
