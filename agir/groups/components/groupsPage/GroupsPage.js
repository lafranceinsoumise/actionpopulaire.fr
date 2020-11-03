import React from "react";
import PropTypes from "prop-types";
import styled from "styled-components";
import GroupCard from "@agir/groups/groupComponents/GroupCard";
import { DateTime } from "luxon";

const Container = styled.div`
  margin: 0 auto;
  max-width: 600px;
`;

const GroupsPage = ({ data }) => {
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
    <Container>
      {groups.map((group) => (
        <GroupCard key={group.id} {...group} />
      ))}
    </Container>
  );
};

GroupsPage.propTypes = { data: PropTypes.arrayOf(GroupCard.propTypes) };

export default GroupsPage;
