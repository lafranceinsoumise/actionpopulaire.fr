import PropTypes from "prop-types";
import React from "react";
import useSWRImmutable from "swr/immutable";

import Redirect from "@agir/front/app/Redirect";

import { groupUpcomingEventLinkForGroup } from "./common";

const GroupUpcomingEventRedirectPage = ({ groupPk }) => {
  const { data: group, isLoading } = useSWRImmutable(
    groupPk && `/api/groupes/${groupPk}/`,
  );

  if (isLoading || typeof group === "undefined") {
    return null;
  }

  const groupDetailsRoute = {
    route: "groupDetails",
    routeParams: { groupPk },
  };

  const groupUpcomingEventLink = groupUpcomingEventLinkForGroup(group);

  if (groupUpcomingEventLink) {
    return (
      <Redirect to={groupUpcomingEventLink} backLink={groupDetailsRoute} />
    );
  }

  return <Redirect {...groupDetailsRoute} />;
};

GroupUpcomingEventRedirectPage.propTypes = {
  groupPk: PropTypes.string,
};

export default GroupUpcomingEventRedirectPage;
