import PropTypes from "prop-types";
import React from "react";

import GroupList from "./GroupList";
import GroupCard from "@agir/groups/groupComponents/GroupCard";
import Onboarding from "@agir/front/genericComponents/Onboarding";

import { useSelector } from "@agir/front/globalContext/GlobalContext";
import { getRoutes } from "@agir/front/globalContext/reducers";

const GroupSuggestions = ({ groups }) => {
  const routes = useSelector(getRoutes);

  return (
    <div style={{ paddingBottom: 64 }}>
      <Onboarding type="group__suggestions" routes={routes} />
      {Array.isArray(groups) && groups.length > 0 && (
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
      <Onboarding type="group__creation" routes={routes} />
    </div>
  );
};

GroupSuggestions.propTypes = {
  groups: PropTypes.arrayOf(PropTypes.object),
};

export default GroupSuggestions;
