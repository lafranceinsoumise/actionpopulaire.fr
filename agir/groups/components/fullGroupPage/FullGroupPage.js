import PropTypes from "prop-types";
import React from "react";
import styled from "styled-components";

import Card from "@agir/front/genericComponents/Card";
import GroupCard from "@agir/groups/groupComponents/GroupCard";
import Onboarding from "@agir/front/genericComponents/Onboarding";
import CenteredLayout from "@agir/front/dashboardComponents/CenteredLayout";

import style from "@agir/front/genericComponents/_variables.scss";
import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes } from "@agir/front/globalContext/reducers";

const StyledBlock = styled.article`
  padding: 0;
  margin-bottom: 2rem;

  @media (max-width: ${style.collapse}px) {
    padding: 0 25px;
    margin-bottom: 1rem;
  }

  p {
    margin: 0 0 1rem;
  }
`;

const Map = styled.iframe`
  margin: 0;
  padding: 0;
  width: 100%;
  height: 338px;
  border: none;
  overflow: hidden;
`;

const GroupList = styled.article`
  margin-top: 2rem;
  margin-bottom: 2rem;

  @media (max-width: ${style.collapse}px) {
    padding: 0 1rem;
  }

  & > ${Card} {
    margin-bottom: 1rem;
  }
`;

const FullGroupPage = ({ fullGroup, groupSuggestions }) => {
  const routes = useSelector(getRoutes);

  return (
    <CenteredLayout
      title={`${fullGroup.name} compte déjà trop de membres !`}
      icon="x-circle"
    >
      <StyledBlock>
        <p>Désolé, vous ne pouvez pas rejoindre ce groupe.</p>
        <p>
          Pour favoriser l'implication de chacun·e et la répartition de l'action
          sur le tout le territoire, nous privilégions les petites équipes.
        </p>
        <p>Rejoignez une autre équipe proche de chez vous&nbsp;:</p>
      </StyledBlock>
      {routes.groupsMap ? <Map src={routes.groupsMap} /> : null}
      {Array.isArray(groupSuggestions) && groupSuggestions.length > 0 && (
        <GroupList>
          {groupSuggestions.map((group) => (
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
      <Onboarding type="fullGroup__creation" routes={routes} />
    </CenteredLayout>
  );
};

FullGroupPage.propTypes = {
  fullGroup: PropTypes.shape({
    name: PropTypes.string.isRequired,
  }).isRequired,
  groupSuggestions: PropTypes.arrayOf(PropTypes.shape(GroupCard.propTypes)),
};

export default FullGroupPage;
