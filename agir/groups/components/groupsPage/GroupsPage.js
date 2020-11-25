import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Card from "@agir/front/genericComponents/Card";
import GroupCard from "@agir/groups/groupComponents/GroupCard";
import GroupOnboarding from "@agir/groups/groupComponents/GroupOnboarding";
import { DateTime } from "luxon";
import Layout, { LayoutTitle } from "@agir/front/dashboardComponents/Layout";
import Button from "@agir/front/genericComponents/Button";

import style from "@agir/front/genericComponents/_variables.scss";
import { useGlobalContext } from "@agir/front/genericComponents/GlobalContext";

const TopBar = styled.div`
  display: flex;
  flex-flow: row wrap;
  justify-content: space-between;
  margin: 0 0 25px;

  & > h1 {
    margin: 0 0 1rem;

    @media (max-width: ${style.collapse}px) {
      flex: 0 0 100%;
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
  margin-bottom: 60px;

  @media (max-width: ${style.collapse}px) {
    padding: 0 16px;
  }

  & > ${Card} {
    margin-bottom: 16px;
  }
`;

const GroupsPage = ({ data }) => {
  const { routes } = useGlobalContext();
  const groups = React.useMemo(
    () =>
      data.map(({ discountCodes, ...group }) => ({
        ...group,
        discountCodes: discountCodes.map(({ code, expirationDate }) => ({
          code,
          expirationDate: DateTime.fromISO(expirationDate, {
            zone: "Europe/Paris",
            locale: "fr",
          }),
        })),
      })),
    [data]
  );

  if (groups.length === 0) {
    return (
      <Layout active="groups">
        <TopBar>
          <LayoutTitle>Groupes</LayoutTitle>
        </TopBar>
        <GroupOnboarding type="action" routes={routes} />
      </Layout>
    );
  }

  return (
    <Layout active="groups" smallBackgroundColor={style.black25}>
      <TopBar>
        <LayoutTitle>Mes groupes</LayoutTitle>
        <div>
          <Button
            as="a"
            href={routes.createGroup}
            icon="plus"
            color="secondary"
            small
          >
            Créer un groupe
          </Button>
          <Button as="a" icon="map" href={routes.groupsMap} small color="white">
            Carte
          </Button>
        </div>
      </TopBar>
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
      {groups.every(({ type }) => type !== "B") ? (
        <GroupOnboarding type="thematic" routes={routes} />
      ) : null}
    </Layout>
  );
};

GroupsPage.propTypes = {
  data: PropTypes.arrayOf(PropTypes.shape(GroupCard.propTypes)),
};

export default GroupsPage;
