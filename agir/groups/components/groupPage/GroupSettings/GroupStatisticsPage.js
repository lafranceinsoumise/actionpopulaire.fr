import PropTypes from "prop-types";
import React, { useState } from "react";
import styled from "styled-components";
import useSWRImmutable from "swr/immutable";

import { getGroupEndpoint } from "@agir/groups/utils/api";

import SelectField from "@agir/front/formComponents/SelectField";
import HeaderPanel from "@agir/front/genericComponents/ObjectManagement/HeaderPanel";
import {
  h3,
  StyledTitle,
} from "@agir/front/genericComponents/ObjectManagement/styledComponents";
import PageFadeIn from "@agir/front/genericComponents/PageFadeIn";
import { RawFeatherIcon } from "@agir/front/genericComponents/FeatherIcon";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import Spacer from "@agir/front/genericComponents/Spacer";
import FaIcon from "@agir/front/genericComponents/FaIcon";

const PERIOD_CHOICE = [
  { value: "month", label: "Depuis le début du mois" },
  { value: "year", label: "Depuis le début de l'année" },
  { value: "last_month", label: "Le mois dernier" },
  { value: "last_year", label: "L'année dernière" },
  { value: "ever", label: "Depuis la création du groupe" },
];

const StyledSkeleton = styled(Skeleton)`
  &:nth-child(odd) {
    height: 2rem;
    max-width: 50%;
    margin-bottom: 1rem;
  }
`;
const StyledCard = styled.div`
  display: flex;
  flex-flow: row nowrap;
  gap: 1rem;
  align-items: center;
  padding: 1rem;
  border: 1px solid ${(props) => props.theme.text100};

  & > * {
    flex: 0 0 auto;
  }

  & > strong {
    flex: 1 1 auto;
    font-weight: 400;
    font-size: 1rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 0.875rem;
    }
  }

  & > span {
    font-size: 2rem;
    font-weight: normal;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 1rem;
      font-weight: 600;
    }
  }

  & > ${RawFeatherIcon} {
    color: ${(props) => props.theme.primary500};
    width: 2rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      width: 1rem;
    }
  }
`;

const StyledSubtypeCard = styled.div`
  display: flex;
  flex-flow: row-reverse wrap;
  justify-content: start;
  gap: 0 1rem;

  & + & {
    @media (max-width: ${(props) => props.theme.collapse}px) {
      margin-top: 0.5rem;
    }
  }

  & > p {
    flex: 0 0 auto;
    font-size: 0.875rem;
    line-height: 1.5;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding-bottom: 0.25rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      flex: 0 0 100%;
    }

    & > * {
      flex: 0 0 auto;
    }

    & > span {
      flex: 1 1 100%;
    }
  }

  & > div {
    flex: 0 0 ${(props) => props.$ratio}%;
    background-color: ${(props) => props.$color};
    height: 2.5rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      height: 1.5rem;
    }
  }
`;

const StyledLocationCard = styled.div`
  padding: 1rem;
  border: 1px solid ${(props) => props.theme.text100};
  display: flex;
  flex-flow: row nowrap;
  gap: 1rem;
  align-items: center;

  & > ${RawFeatherIcon} {
    color: ${(props) => props.theme.primary500};
    background-color: ${(props) => props.theme.primary50};
    border-radius: 100%;
    padding: 12px;
  }

  & > p {
    margin: 0;
    display: flex;
    flex-flow: column nowrap;
    gap: 0.25rem;

    @media (max-width: ${(props) => props.theme.collapse}px) {
      font-size: 0.875rem;
    }

    strong {
      font-weight: 600;

      @media (max-width: ${(props) => props.theme.collapse}px) {
        font-weight: 500;
      }
    }

    span {
      color: ${(props) => props.theme.text500};
    }
  }
`;

const StyledContent = styled.div`
  display: flex;
  flex-direction: column;
  gap: 0.5rem;

  h3 {
    font-size: 1rem;
    margin: 0;
  }
`;

const GroupStatisticsPage = (props) => {
  const { groupPk, onBack, illustration } = props;

  const [period, setPeriod] = useState(PERIOD_CHOICE[0]);

  const { data, isLoading } = useSWRImmutable(
    getGroupEndpoint("getStatistics", { groupPk }, { period: period.value }),
  );

  return (
    <div>
      <HeaderPanel onBack={onBack} illustration={illustration} />
      <StyledTitle style={{ fontSize: "2rem" }}>Statistiques</StyledTitle>
      <Spacer size="1rem" />
      <SelectField
        label="Période"
        helpText=""
        name="period"
        value={period}
        options={PERIOD_CHOICE}
        onChange={setPeriod}
        disabled={isLoading}
      />
      <hr />
      <PageFadeIn ready={!isLoading} wait={<StyledSkeleton boxes={6} />}>
        {!!data && (
          <StyledContent>
            <h3>Événements</h3>
            <StyledCard>
              <strong>Événements organisés</strong>
              <span>{data.events.count}</span>
              <RawFeatherIcon name="calendar" />
            </StyledCard>
            <StyledCard>
              <strong>Moyenne d'événements par mois</strong>
              <span>
                {(
                  Math.round(data.events.averageByMonth * 100) / 100
                ).toLocaleString()}
              </span>
              <RawFeatherIcon name="plus" />
            </StyledCard>
            <StyledCard>
              <strong>Nombre moyen de participant·es</strong>
              <span>{Math.round(data.events.averageParticipants)}</span>
              <RawFeatherIcon name="users" />
            </StyledCard>

            <Spacer size="1rem" />

            <h3>Vie du groupe</h3>
            <StyledCard>
              <strong>Nouveaux membres actifs</strong>
              <span>{data.members.active}</span>
              <RawFeatherIcon name="user-check" />
            </StyledCard>
            <StyledCard>
              <strong>Nombre d'heures militées</strong>
              <span>
                {Math.round(data.events.totalDuration / 3600).toLocaleString()}
              </span>
              <RawFeatherIcon name="clock" />
            </StyledCard>
            <StyledCard>
              <strong>Nombre de messages envoyés</strong>
              <span>{data.messages.count.toLocaleString()}</span>
              <RawFeatherIcon name="mail" />
            </StyledCard>
            <StyledCard>
              <strong>Contacts ajoutés</strong>
              <span>{data.members.followers.toLocaleString()}</span>
              <RawFeatherIcon name="user-plus" />
            </StyledCard>

            {data.events.topSubtypes.length > 0 && (
              <>
                <Spacer size="2rem" />
                <h3>Types d'événement les plus utilisés</h3>
                <Spacer size="0" />
                {data.events.topSubtypes.map((subtype) => (
                  <StyledSubtypeCard
                    key={subtype}
                    $color={subtype.color}
                    $ratio={Math.min(
                      Math.round((subtype.events / data.events.count) * 100),
                      100,
                    )}
                  >
                    <p>
                      <FaIcon
                        color={subtype.color}
                        size="1rem"
                        icon={subtype.iconName}
                      />
                      <span>
                        {subtype.description} ({subtype.events})
                      </span>
                    </p>
                    <div aria-hidden={true} />
                  </StyledSubtypeCard>
                ))}
              </>
            )}
            {data.events.topLocations.length > 0 && (
              <>
                <Spacer size="2rem" />
                <h3>Lieux les plus fréquentés par le groupe</h3>
                <Spacer size="0" />
                {data.events.topLocations.map((location) => (
                  <StyledLocationCard key={location}>
                    <RawFeatherIcon name="map-pin" />
                    <p>
                      <strong>
                        {location.address.split("\n")[0]} ({location.events})
                      </strong>
                      <span>{location.address.split("\n")[1]}</span>
                    </p>
                  </StyledLocationCard>
                ))}
              </>
            )}
          </StyledContent>
        )}
      </PageFadeIn>
    </div>
  );
};
GroupStatisticsPage.propTypes = {
  onBack: PropTypes.func,
  illustration: PropTypes.string,
  groupPk: PropTypes.string,
};
export default GroupStatisticsPage;
