import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import GroupCard from "@agir/groups/groupComponents/GroupCard";
import { DateTime } from "luxon";
import Layout, { LayoutTitle } from "@agir/front/dashboardComponents/Layout";
import { Column, Row } from "@agir/front/genericComponents/grid";
import Button from "@agir/front/genericComponents/Button";

import style from "@agir/front/genericComponents/_variables.scss";
import { useGlobalContext } from "@agir/front/genericComponents/GobalContext";

const ButtonHolder = styled(Column)`
  display: flex;
  align-items: center;

  * {
    margin-left: 0.5rem;
  }

  @media only screen and (min-width: ${style.collapse}px) {
    > *:first-child {
      order: 1;
    }
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
      <Row style={{ margin: "0 0 1.5rem" }}>
        <Column width={["100%", "content"]} grow>
          <LayoutTitle>Mes groupes</LayoutTitle>
        </Column>
        <ButtonHolder>
          <Button
            as="a"
            href={routes.createGroup}
            icon="plus"
            color="secondary"
            small
          >
            Créer un groupe
          </Button>
          <Button as="a" icon="map" href={routes.groupsMap} small>
            Carte
          </Button>
        </ButtonHolder>
      </Row>
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
    </Layout>
  );
};

GroupsPage.propTypes = {
  data: PropTypes.arrayOf(PropTypes.shape(GroupCard.propTypes)),
};

export default GroupsPage;
