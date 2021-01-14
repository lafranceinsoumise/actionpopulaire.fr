import { DateTime } from "luxon";
import PropTypes from "prop-types";
import React from "react";
import { Helmet } from "react-helmet";
import styled from "styled-components";
import useSWR from "swr";

import style from "@agir/front/genericComponents/_variables.scss";

import Card from "@agir/front/genericComponents/Card";
import GroupCard from "@agir/groups/groupComponents/GroupCard";
import Onboarding from "@agir/front/genericComponents/Onboarding";
import { LayoutTitle } from "@agir/front/dashboardComponents/Layout";
import Button from "@agir/front/genericComponents/Button";
import Skeleton from "@agir/front/genericComponents/Skeleton";
import { PageFadeIn } from "@agir/front/genericComponents/PageFadeIn";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import {
  getRoutes,
  getIsSessionLoaded,
} from "@agir/front/globalContext/reducers";

const TopBar = styled.div`
  display: flex;
  flex-flow: row wrap;
  justify-content: space-between;
  margin: 0 0 25px;

  & > ${LayoutTitle} {
    margin: 0;

    @media (max-width: ${style.collapse}px) {
      flex: 0 0 100%;
      margin-bottom: 1rem;
    }
  }

  & > div {
    display: flex;
    flex-direction: row-reverse;
    align-items: center;

    @media only screen and (max-width: ${style.collapse}px) {
      flex-direction: row;
      margin-left: 1.5rem;
      margin-right: 1.5rem;
    }
  }

  & ${Button} + ${Button} {
    @media only screen and (min-width: ${style.collapse}px) {
      margin-right: 0.5rem;
    }
    @media only screen and (max-width: ${style.collapse}px) {
      margin-left: 0.5rem;
    }
  }
`;

const GroupList = styled.article`
  margin-bottom: 2rem;

  @media (max-width: ${style.collapse}px) {
    padding: 0 16px;
  }

  & > ${Card} {
    margin-bottom: 16px;
  }
`;

const GroupsPage = () => {
  const routes = useSelector(getRoutes);
  const isSessionLoaded = useSelector(getIsSessionLoaded);

  const { data: groupList } = useSWR("/api/groupes");

  const groups = React.useMemo(
    () =>
      groupList
        ? groupList.map(({ discountCodes, ...group }) => ({
            ...group,
            discountCodes: discountCodes.map(({ code, expirationDate }) => ({
              code,
              expirationDate: DateTime.fromISO(expirationDate, {
                zone: "Europe/Paris",
                locale: "fr",
              }),
            })),
          }))
        : [],
    [groupList]
  );

  const hasOwnGroups = React.useMemo(
    () => groups && groups.some((group) => group.isMember),
    [groups]
  );

  return (
    <>
      <Helmet>
        <title>Mes groupes - Action populaire</title>
      </Helmet>
      <TopBar>
        <LayoutTitle>Mes groupes</LayoutTitle>
        <div>
          {routes.createGroup ? (
            <Button
              as="a"
              href={routes.createGroup}
              icon="plus"
              color="secondary"
              small
            >
              Créer un groupe
            </Button>
          ) : null}
          {routes.groupMapPage ? (
            <Button as="Link" icon="map" route="groupMapPage" small>
              Carte
            </Button>
          ) : null}
        </div>
      </TopBar>
      <PageFadeIn
        ready={isSessionLoaded && groupList}
        wait={<Skeleton boxes={2} />}
      >
        {/* Si l'utilisateurice n'a pas de groupes,
        groups contient la liste des groupes suggérés,
         on place donc avant le texte introductif */}
        {!hasOwnGroups ? (
          <Onboarding type="group__suggestions" routes={routes} />
        ) : null}
        {groups.length > 0 && (
          <GroupList>
            {groups.map((group) => (
              <GroupCard
                key={group.id}
                {...group}
                displayDescription={false}
                displayType={false}
                displayGroupLogo={false}
                displayMembership={false}
              />
            ))}
          </GroupList>
        )}
        {!hasOwnGroups ? (
          <Onboarding type="group__creation" routes={routes} />
        ) : null}
      </PageFadeIn>
    </>
  );
};

GroupsPage.propTypes = {
  groupList: PropTypes.arrayOf(PropTypes.shape(GroupCard.propTypes)),
};

export default GroupsPage;
