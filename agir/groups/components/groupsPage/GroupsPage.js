import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Card from "@agir/front/genericComponents/Card";
import GroupCard from "@agir/groups/groupComponents/GroupCard";
import { DateTime } from "luxon";
import Layout, { LayoutTitle } from "@agir/front/dashboardComponents/Layout";
import Button from "@agir/front/genericComponents/Button";

import style from "@agir/front/genericComponents/_variables.scss";
import { useGlobalContext } from "@agir/front/genericComponents/GobalContext";

const TopBar = styled.div`
  display: flex;
  flex-flow: row wrap;
  justify-content: space-between;
  margin: 0 0 25px;

  @media (max-width: ${style.collapse}px) {
    margin: 25px;
  }

  & > h1 {
    margin: 0 0 16px;

    @media (max-width: ${style.collapse}px) {
      flex: 0 0 100%;
    }
  }

  & ${Button} + ${Button} {
    margin-left: 10px;
  }
`;

const GroupList = styled.article`
  @media (max-width: ${style.collapse}px) {
    padding: 0 16px;
  }

  & > ${Card} {
    margin-bottom: 16px;
    border-radius: 8px;
    box-shadow: 0px 0px 3px rgba(0, 35, 44, 0.1),
      0px 2px 0px rgba(0, 35, 44, 0.08);
  }
`;

const GroupsPage = ({ data }) => {
  const { routes } = useGlobalContext();
  const groups = data.map(({ discountCodes, ...group }) => ({
    ...group,
    discountCodes: discountCodes.map(({ code, expirationDate }) => ({
      code,
      expirationDate: DateTime.fromISO(expirationDate, {
        zone: "Europe/Paris",
        locale: "fr",
      }),
    })),
  }));

  return (
    <Layout active="groups">
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
    </Layout>
  );
};

GroupsPage.propTypes = {
  data: PropTypes.arrayOf(PropTypes.shape(GroupCard.propTypes)),
};

export default GroupsPage;
